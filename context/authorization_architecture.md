# Authorization System Architecture - MeerTime Data Portal

## Executive Summary

This document outlines the complete architecture for transitioning from a role-based authorization system to a project-based authorization system for the MeerTime Data Portal. The implementation is broken into 10 phased merge requests (MRs) designed to minimize breaking changes and allow for incremental deployment.

**Key Changes:**

- Remove global user roles (RESTRICTED, UNRESTRICTED, ADMIN)
- Introduce project-based access control with three membership roles (OWNER, MANAGER, MEMBER)
- Implement access request workflow for users to join projects
- Add email notifications for access requests and approvals
- Maintain backward compatibility during transition

---

## Current System Analysis

### Existing Authorization Structure

- **User Roles**: Three levels (RESTRICTED, UNRESTRICTED, ADMIN)
  - RESTRICTED: No access to embargoed data
  - UNRESTRICTED: Full access to all data
  - ADMIN: Administrative access
- **Embargo System**: Project-level embargo periods (default 18 months)
  - `Project.embargo_period`: Duration field
  - `Observation.embargo_end_date`: Calculated from `utc_start + project.embargo_period`
  - `Observation.is_embargoed()`: Checks if current date is before embargo end
  - `Observation.is_restricted(user)`: Checks if user can access based on role
- **Current Authorization Points**:
  - GraphQL queries: `@user_passes_test(lambda user: user.is_unrestricted())`
  - File downloads/views: Check `is_restricted(user)` or `is_embargoed`
  - Frontend: Display `restricted` field

### Files Impacted by Current System

**Backend:**

- `backend/utils/constants.py` - UserRole enum
- `backend/user_manage/models.py` - User model with role field
- `backend/dataportal/models.py` - Observation.is_restricted(), is_embargoed()
- `backend/dataportal/graphql/queries.py` - Authorization decorators
- `backend/dataportal/views.py` - File access checks
- Migrations in `user_manage` and `dataportal`

**Frontend:**

- GraphQL fragments querying `restricted` field
- UI components conditionally rendering based on restriction status

---

## Finalized Architecture

### Project Membership Roles

The new system introduces three membership roles:

1. **OWNER**: The primary science lead for the project
   - Assigned when the project is created
   - Cannot be removed from the project
   - Can manage all members (add/remove/promote)
   - Can approve/deny access requests
   - One per project

2. **MANAGER**: Project managers with administrative capabilities
   - Can add/remove members
   - Can promote members to MANAGER role
   - Cannot promote members to OWNER
   - Can approve/deny access requests
   - Multiple managers allowed per project

3. **MEMBER**: Regular project members
   - Has access to all project data (including embargoed)
   - Cannot manage other members
   - Cannot approve access requests
   - Multiple members allowed per project

### Authorization Rules

1. **Superusers**: Full access to everything, can manage all projects, override all restrictions
2. **Project Members** (OWNER/MANAGER/MEMBER): Full access to all observations in their projects, regardless of embargo. Can download data.
3. **Logged-in users without project access**: Can view non-embargoed data, can download non-embargoed data, can request access to projects.
4. **Anonymous users**: Can view non-embargoed data, **cannot download or request access**

### Access Request Workflow

1. User browses available projects (logged in users only)
2. User requests access to a project with an optional message
3. Email notification sent to all project OWNERS and MANAGERS
4. Any OWNER or MANAGER can approve/deny the request
5. Email notification sent to user when request is approved/denied
6. If approved, user is added as MEMBER with immediate access
7. Users can withdraw pending requests at any time
8. Users can leave projects at any time without approval

### New Models

#### ProjectMembership

```python
class ProjectMembership(models.Model):
    """Links users to projects with their role"""

    MEMBER = 'MEMBER'
    MANAGER = 'MANAGER'
    OWNER = 'OWNER'

    ROLE_CHOICES = [
        (MEMBER, 'Member'),
        (MANAGER, 'Manager'),
        (OWNER, 'Owner'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_memberships')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default=MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_memberships',
        help_text="User who approved this membership (null for initial owner)"
    )

    class Meta:
        unique_together = ('user', 'project')
        indexes = [
            models.Index(fields=['user', 'project']),
            models.Index(fields=['project', 'role']),
        ]
        verbose_name = "Project Membership"
        verbose_name_plural = "Project Memberships"

    def __str__(self):
        return f"{self.user.username} - {self.project.code} ({self.role})"

    def can_manage_members(self):
        """Check if this member can manage other members"""
        return self.role in [self.MANAGER, self.OWNER]

    def can_promote_to_owner(self):
        """Check if this member can promote others to owner (only owner can)"""
        return False  # No one can change the owner

    def can_promote_to_manager(self):
        """Check if this member can promote others to manager"""
        return self.role in [self.MANAGER, self.OWNER]

    def is_removable(self):
        """Check if this member can be removed from the project"""
        return self.role != self.OWNER

    def clean(self):
        """Validate the membership"""
        from django.core.exceptions import ValidationError

        # Ensure only one owner per project
        if self.role == self.OWNER:
            existing_owner = ProjectMembership.objects.filter(
                project=self.project,
                role=self.OWNER
            ).exclude(pk=self.pk)

            if existing_owner.exists():
                raise ValidationError(
                    f"Project {self.project.code} already has an owner: {existing_owner.first().user.username}"
                )
```

#### ProjectAccessRequest

```python
class ProjectAccessRequest(models.Model):
    """Tracks access requests to projects"""

    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    DENIED = 'DENIED'
    WITHDRAWN = 'WITHDRAWN'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (DENIED, 'Denied'),
        (WITHDRAWN, 'Withdrawn'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_access_requests')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='access_requests')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=PENDING)
    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_access_requests'
    )
    message = models.TextField(blank=True, help_text="User's request message explaining why they need access")
    review_notes = models.TextField(blank=True, help_text="Reviewer's internal notes")

    class Meta:
        # Allow one pending request per user per project
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'project'],
                condition=models.Q(status=PENDING),
                name='unique_pending_request_per_user_project'
            )
        ]
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['project', 'status']),
            models.Index(fields=['requested_at']),
        ]
        verbose_name = "Project Access Request"
        verbose_name_plural = "Project Access Requests"
        ordering = ['-requested_at']

    def __str__(self):
        return f"{self.user.username} -> {self.project.code} ({self.status})"

    def clean(self):
        """Validate the access request"""
        from django.core.exceptions import ValidationError

        # Check if user is already a member
        if ProjectMembership.objects.filter(user=self.user, project=self.project).exists():
            raise ValidationError(
                f"User {self.user.username} is already a member of project {self.project.code}"
            )
```

### Updated Project Model

Add new fields to existing Project model:

```python
class Project(models.Model):
    # ... existing fields (main_project, code, short, embargo_period, description) ...

    # New fields for authorization system
    description = models.TextField(
        blank=True,
        help_text="Project description visible to logged-in users"
    )
    contact_email = models.EmailField(
        blank=True,
        help_text="Project contact email (visible to logged-in users)"
    )

    def get_owner(self):
        """Get the project owner"""
        try:
            membership = self.memberships.get(role=ProjectMembership.OWNER)
            return membership.user
        except ProjectMembership.DoesNotExist:
            return None

    def get_owner_membership(self):
        """Get the project owner membership object"""
        try:
            return self.memberships.get(role=ProjectMembership.OWNER)
        except ProjectMembership.DoesNotExist:
            return None

    def get_leads(self):
        """Get all project leads (managers and owner)"""
        return self.memberships.filter(
            role__in=[ProjectMembership.MANAGER, ProjectMembership.OWNER]
        ).select_related('user')

    def get_all_members(self):
        """Get all project members"""
        return self.memberships.all().select_related('user')

    def get_member_count(self):
        """Get total number of members"""
        return self.memberships.count()
```

### Updated User Model

Add helper methods (keep existing `role` field during transition):

```python
class User(AbstractUser):
    # ... existing fields including role ...

    def get_project_memberships(self):
        """Get all project memberships for this user"""
        return self.project_memberships.select_related('project').all()

    def can_access_project(self, project):
        """Check if user can access a project's data"""
        if self.is_superuser:
            return True
        return self.project_memberships.filter(project=project).exists()

    def is_project_lead(self, project):
        """Check if user is a manager or owner of the project"""
        if self.is_superuser:
            return True
        return self.project_memberships.filter(
            project=project,
            role__in=[ProjectMembership.MANAGER, ProjectMembership.OWNER]
        ).exists()

    def is_project_owner(self, project):
        """Check if user is the owner of the project"""
        if self.is_superuser:
            return True
        return self.project_memberships.filter(
            project=project,
            role=ProjectMembership.OWNER
        ).exists()

    def get_accessible_projects(self):
        """Get all projects this user can access"""
        if self.is_superuser:
            from dataportal.models import Project
            return Project.objects.all()
        return Project.objects.filter(memberships__user=self)

    def has_any_project_access(self):
        """Check if user has access to any projects"""
        if self.is_superuser:
            return True
        return self.project_memberships.exists()

    def get_led_projects(self):
        """Get all projects where user is a manager or owner"""
        return Project.objects.filter(
            memberships__user=self,
            memberships__role__in=[ProjectMembership.MANAGER, ProjectMembership.OWNER]
        )
```

### Updated Observation Model

Add new authorization methods (keep `is_restricted` for backward compatibility during transition):

```python
class Observation(models.Model):
    # ... existing fields ...

    def can_user_access(self, user):
        """
        Check if the user can access (view) this observation.

        Rules:
        - Superusers: Always can access
        - Project members: Can access regardless of embargo
        - Other logged-in users: Can only access non-embargoed data
        - Anonymous users: Can only access non-embargoed data

        :param user: Django user instance (can be anonymous)
        :return: bool
        """
        # Superusers have full access
        if user.is_authenticated and user.is_superuser:
            return True

        # Project members have full access (including embargoed data)
        if user.is_authenticated and user.can_access_project(self.project):
            return True

        # Everyone else can only access non-embargoed data
        return not self.is_embargoed()

    def can_user_download(self, user):
        """
        Check if the user can download files from this observation.
        Only authenticated users with project access can download.

        :param user: Django user instance
        :return: bool
        """
        if not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        return user.can_access_project(self.project)

    # Keep old method for backward compatibility (will be removed in Phase 9)
    def is_restricted(self, user):
        """DEPRECATED: Use can_user_access() instead"""
        return not self.can_user_access(user)
```

---

## Implementation Plan - Phased MRs

### Phase 1: Foundation & Models (MR #1)

**Goal**: Create new database models and update Project model without breaking existing functionality

**Tasks**:

1. Add new fields to Project model:
   - `description` (TextField, blank=True)
   - `contact_email` (EmailField, blank=True)
   - Add helper methods: `get_owner()`, `get_leads()`, `get_all_members()`, etc.

2. Create new models:
   - `ProjectMembership` with all fields, methods, and validation
   - `ProjectAccessRequest` with all fields and methods

3. Create database migrations

4. Add comprehensive model tests:
   - Test ProjectMembership creation and validation
   - Test one owner per project constraint
   - Test ProjectAccessRequest creation and unique constraint
   - Test Project helper methods

5. Update admin interface:
   - Register ProjectMembership with inline editing
   - Register ProjectAccessRequest with list filters
   - Update Project admin to show memberships inline

**Files Created/Modified**:

- `backend/dataportal/models.py` - Add ProjectMembership, ProjectAccessRequest, update Project
- `backend/dataportal/migrations/XXXX_add_project_authorization.py` - New migration
- `backend/dataportal/admin.py` - Register new models
- `backend/dataportal/tests/test_authorization_models.py` - New test file

**Acceptance Criteria**:

- All migrations run successfully
- All tests pass
- Can create project memberships via Django admin
- One owner per project constraint enforced
- No impact on existing authorization (old User.role still works)

**No breaking changes**: Existing authorization still works via old `User.role` field

---

### Phase 2: Helper Methods & Utilities (MR #2)

**Goal**: Add new authorization helper methods alongside old ones

**Tasks**:

1. Add User model methods (in `user_manage/models.py`):
   - `get_project_memberships()`
   - `can_access_project(project)`
   - `is_project_lead(project)`
   - `is_project_owner(project)`
   - `get_accessible_projects()`
   - `has_any_project_access()`
   - `get_led_projects()`

2. Add Observation model methods (in `dataportal/models.py`):
   - `can_user_access(user)` - new project-based logic
   - `can_user_download(user)` - download permission check
   - Keep `is_restricted(user)` as deprecated wrapper

3. Create utility module for authorization helpers:
   - Permission checking decorators
   - Helper functions for common authorization patterns

4. Add comprehensive tests:
   - Test all User helper methods with different scenarios
   - Test all Observation authorization methods
   - Test with superusers, members, non-members, anonymous users
   - Test edge cases (no owner, user in multiple projects, etc.)

**Files Created/Modified**:

- `backend/user_manage/models.py` - Add User helper methods
- `backend/dataportal/models.py` - Add Observation helper methods
- `backend/utils/authorization.py` - New utility module
- `backend/user_manage/tests/test_user_authorization.py` - New test file
- `backend/dataportal/tests/test_observation_authorization.py` - New test file

**Acceptance Criteria**:

- All new methods work correctly
- Backward compatibility maintained (old methods still work)
- All tests pass (including existing tests)
- Code coverage for new methods > 90%

**No breaking changes**: Old methods remain, new methods added

---

### Phase 3: GraphQL Schema Updates (MR #3)

**Goal**: Add GraphQL queries/mutations for new authorization system

**Tasks**:

1. Add new GraphQL types:
   - `ProjectMembershipNode` (DjangoObjectType)
   - `ProjectAccessRequestNode` (DjangoObjectType)
   - Update `ProjectNode` to include new fields (description, contact_email, member_count)

2. Add queries:
   - `myProjectMemberships` - Current user's memberships
   - `myProjectAccessRequests` - Current user's pending/historical requests
   - `projectMembers(projectId)` - List members (visible to leads only)
   - `projectAccessRequests(projectId)` - List pending requests (leads only)
   - `availableProjects` - Projects user can request access to

3. Add mutations:
   - `requestProjectAccess(projectId, message)` - Request access
   - `withdrawAccessRequest(requestId)` - Withdraw pending request
   - `approveProjectAccess(requestId, notes)` - Approve request (lead only)
   - `denyProjectAccess(requestId, notes)` - Deny request (lead only)
   - `removeProjectMember(membershipId)` - Remove member (lead only)
   - `promoteToManager(membershipId)` - Promote to manager (lead only)
   - `leaveProject(projectId)` - User leaves project

4. Add authorization decorators:
   - `@project_lead_required` - Must be project lead
   - `@project_member_required` - Must be project member

5. Add comprehensive tests:
   - Test all queries with different user roles
   - Test all mutations with permissions
   - Test error cases (unauthorized, invalid data, etc.)

**Files Created/Modified**:

- `backend/dataportal/graphql/types/` - New type files
- `backend/dataportal/graphql/queries.py` - New queries
- `backend/dataportal/graphql/mutations/project_authorization.py` - New mutations
- `backend/dataportal/graphql/decorators.py` - New decorators
- `backend/dataportal/graphql/tests/test_project_authorization_graphql.py` - New tests

**Acceptance Criteria**:

- GraphQL schema updated successfully
- All queries return correct data
- All mutations work with proper authorization
- Unauthorized access properly rejected
- All tests pass

**No breaking changes**: Only additions to GraphQL schema

---

### Phase 4: Frontend - Project Access UI (MR #4)

**Goal**: Build UI for users to request and manage project access

**Tasks**:

1. Create components:
   - `ProjectList.jsx` - Browse available projects with descriptions
   - `ProjectAccessRequestButton.jsx` - Request access button with modal
   - `MyProjectMemberships.jsx` - Show user's current projects
   - `MyAccessRequests.jsx` - Show pending/historical requests
   - `ProjectCard.jsx` - Display project info card

2. Update Profile/Settings page:
   - Add "My Projects" section showing memberships
   - Add "Access Requests" section showing request status
   - Add "Leave Project" functionality

3. Add new routes:
   - `/projects` - Browse projects (logged-in only)

4. Implement Relay queries/mutations:
   - Update schema with `npm run relay`
   - Implement query components
   - Implement mutation hooks

5. Add user feedback:
   - Success/error toast notifications
   - Loading states
   - Confirmation modals for actions

6. Add tests:
   - Component rendering tests
   - User interaction tests
   - Form submission tests

**Files Created/Modified**:

- `frontend/src/components/projects/ProjectList.jsx`
- `frontend/src/components/projects/ProjectCard.jsx`
- `frontend/src/components/projects/ProjectAccessRequestButton.jsx`
- `frontend/src/components/projects/MyProjectMemberships.jsx`
- `frontend/src/components/projects/MyAccessRequests.jsx`
- `frontend/src/pages/Projects.jsx`
- `frontend/src/pages/Profile.jsx` - Update with new sections
- `frontend/src/__generated__/` - Relay artifacts
- `frontend/src/tests/` - Frontend tests

**Acceptance Criteria**:

- Users can browse projects
- Users can request access with a message
- Users can see their memberships and requests
- Users can withdraw pending requests
- Users can leave projects
- All UI elements responsive and accessible

**No breaking changes**: Only new UI pages

---

### Phase 5: Frontend - Project Lead Management UI (MR #5)

**Goal**: Build UI for project leads to manage access requests and members

**Tasks**:

1. Create components:
   - `ProjectManagementDashboard.jsx` - Overview for leads
   - `AccessRequestList.jsx` - Pending requests with approve/deny
   - `ProjectMemberList.jsx` - Current members with management options
   - `AccessRequestReviewModal.jsx` - Review request with notes

2. Add lead-specific functionality:
   - Approve/deny access requests
   - Remove members
   - Promote members to manager
   - View member join dates and who approved them

3. Add authorization checks:
   - Only show management UI to leads
   - Hide owner removal option
   - Conditional rendering based on role

4. Add notification indicators:
   - Badge showing pending request count
   - Highlight for new requests

5. Add tests:
   - Lead dashboard rendering
   - Access request approval/denial
   - Member management actions
   - Authorization checks

**Files Created/Modified**:

- `frontend/src/components/projects/ProjectManagementDashboard.jsx`
- `frontend/src/components/projects/AccessRequestList.jsx`
- `frontend/src/components/projects/ProjectMemberList.jsx`
- `frontend/src/components/projects/AccessRequestReviewModal.jsx`
- `frontend/src/pages/ProjectManagement.jsx`
- `frontend/src/components/navigation/` - Add link for leads
- `frontend/src/tests/` - Lead workflow tests

**Acceptance Criteria**:

- Leads can see all pending requests for their projects
- Leads can approve/deny requests with notes
- Leads can manage project members
- Leads can promote members to manager
- Owner cannot be removed
- Non-leads cannot access management UI

**No breaking changes**: Only new UI for leads

---

### Phase 6: Email Notification System (MR #6)

**Goal**: Notify users of access request status changes via email

**Tasks**:

1. Create email templates:
   - `access_request_created.html/txt` - Notify leads of new request
   - `access_request_approved.html/txt` - Notify user of approval
   - `access_request_denied.html/txt` - Notify user of denial
   - Base email template with MeerTime branding

2. Create notification service:
   - `notifications.py` with email sending functions
   - Handle email configuration
   - Error handling and logging

3. Add Django signals:
   - Post-save signal on ProjectAccessRequest for status changes
   - Trigger appropriate email based on status

4. Configure email settings:
   - Add email backend configuration
   - Add SMTP settings to .env template
   - Add email sender address configuration

5. Add tests:
   - Test email content generation
   - Test signal triggering
   - Mock email sending in tests

**Files Created/Modified**:

- `backend/dataportal/notifications.py` - Email logic
- `backend/dataportal/signals.py` - Signal handlers
- `backend/templates/emails/access_request_created.html`
- `backend/templates/emails/access_request_created.txt`
- `backend/templates/emails/access_request_approved.html`
- `backend/templates/emails/access_request_approved.txt`
- `backend/templates/emails/access_request_denied.html`
- `backend/templates/emails/access_request_denied.txt`
- `backend/templates/emails/base_email.html`
- `backend/meertime/settings/email.py` - Email configuration
- `backend/.env.template` - Add email settings
- `backend/dataportal/tests/test_notifications.py` - New tests

**Acceptance Criteria**:

- Emails sent when access requested (to leads)
- Emails sent when request approved (to user)
- Emails sent when request denied (to user)
- Email templates look professional
- All emails contain relevant information
- Email sending doesn't block request processing

**No breaking changes**: Only additions

---

### Phase 7: Migration Script & Documentation (MR #7)

**Goal**: Prepare for transition - create migration tools and documentation

**Tasks**:

1. Create management command `migrate_authorization.py`:
   - Inventory all current users with their roles
   - Generate report of users and their current access
   - Provide dry-run mode
   - Provide option to convert all UNRESTRICTED users to normal users
   - Log all changes

2. Create migration documentation:
   - `authorization_migration.md` - Technical migration guide
   - `user_communication.md` - User-facing announcement template
   - Rollback procedure
   - Testing checklist

3. Create user communication materials:
   - Email announcement template
   - FAQ document
   - Instructions for requesting project access

4. Create admin setup script:
   - Script to initialize project owners via Django shell
   - Template for setting up initial project memberships

5. Test migration:
   - Run on staging/dev environment
   - Verify data integrity
   - Test rollback procedure

**Files Created/Modified**:

- `backend/user_manage/management/commands/migrate_authorization.py`
- `docs/authorization_migration.md`
- `docs/user_communication_template.md`
- `docs/admin_setup_guide.md`
- `docs/faq_project_access.md`
- `backend/user_manage/tests/test_migration_command.py`

**Acceptance Criteria**:

- Migration command runs successfully
- Dry-run mode works correctly
- All users inventoried
- Documentation complete and clear
- Rollback procedure documented
- Communication materials ready

**No breaking changes**: Preparation only, no system changes

---

### Phase 8: Switch Authorization Logic (MR #8)

**Goal**: Replace old authorization checks with new project-based checks

⚠️ **CRITICAL TRANSITION POINT** - Requires careful testing and staged deployment

**Tasks**:

1. Update GraphQL queries:
   - Replace `@user_passes_test(lambda user: user.is_unrestricted())`
   - Use `@project_member_required` or `can_user_access()` checks
   - Update file queries to use `can_user_download()`

2. Update views:
   - Replace `is_restricted(user)` calls with `can_user_access(user)`
   - Add download permission checks with `can_user_download(user)`
   - Update error messages to reference project membership

3. Update frontend GraphQL queries:
   - Remove `restricted` field usage
   - Add project membership checks where needed
   - Update UI to show project-based access status

4. Add comprehensive integration tests:
   - Test complete workflows (request → approve → access → download)
   - Test all user types (superuser, member, non-member, anonymous)
   - Test edge cases
   - Performance testing for permission checks

5. Update inline comments and deprecation warnings:
   - Mark old authorization code as deprecated
   - Add migration notes

**Files Modified**:

- `backend/dataportal/graphql/queries.py` - Update authorization
- `backend/dataportal/views.py` - Update authorization checks
- `backend/dataportal/graphql/decorators.py` - Add new decorators
- `frontend/src/**/*.jsx` - Update components
- `backend/dataportal/tests/test_authorization_integration.py` - Integration tests

**Pre-Deployment Checklist**:

- [ ] All tests pass
- [ ] Performance testing completed
- [ ] Staging environment tested
- [ ] User communication sent
- [ ] Project owners assigned
- [ ] Rollback procedure ready
- [ ] Monitoring in place

**Deployment Steps**:

1. Deploy to staging
2. Run migration command in dry-run mode
3. Verify staging works correctly
4. Send user communication (1 week notice)
5. Assign project owners via admin script
6. Deploy to production during low-traffic window
7. Monitor for issues
8. Be ready to rollback if needed

**Acceptance Criteria**:

- All authorization checks use new system
- Anonymous users can view non-embargoed data
- Project members can access and download project data
- Non-members cannot download embargoed data
- All integration tests pass
- No performance degradation

**BREAKING CHANGE**: This switches to new authorization system. All users lose unrestricted access and must request project access.

---

### Phase 9: Deprecation & Cleanup (MR #9)

**Goal**: Remove old authorization code after new system is stable

⚠️ **Deploy only after Phase 8 has been stable for at least 2 weeks**

**Tasks**:

1. Remove deprecated User model code:
   - `role` field (create migration)
   - `is_unrestricted()` method

2. Remove deprecated Observation model code:
   - `is_restricted(user)` method

3. Update UserRole enum:
   - Remove `RESTRICTED` and `UNRESTRICTED` values
   - Keep only values needed for other purposes (if any)

4. Remove old tests:
   - Tests for deprecated role-based authorization
   - Update remaining tests

5. Update database:
   - Migration to drop `role` column from User table
   - Clean up old role data

6. Update documentation:
   - Remove references to old system
   - Update API documentation

**Files Modified**:

- `backend/user_manage/models.py` - Remove role field
- `backend/utils/constants.py` - Update UserRole enum
- `backend/dataportal/models.py` - Remove is_restricted
- `backend/user_manage/migrations/XXXX_remove_user_role.py` - New migration
- All test files - Clean up old tests
- Documentation files

**Pre-Deployment Checklist**:

- [ ] Phase 8 stable for 2+ weeks
- [ ] No reported issues with new system
- [ ] All users successfully migrated
- [ ] Backup of database taken

**Acceptance Criteria**:

- Old authorization code removed
- All tests pass
- Database migration successful
- No references to old role system
- Documentation updated

**BREAKING CHANGE**: Old authorization code removed. No rollback to old system possible after this.

---

### Phase 10: Documentation & Polish (MR #10)

**Goal**: Complete documentation and final improvements

**Tasks**:

1. Update README:
   - Explain new authorization system
   - Update setup instructions

2. Create comprehensive guides:
   - User guide for requesting project access
   - Admin guide for managing projects
   - Project lead guide for managing members
   - API documentation with authorization examples

3. Create admin tools:
   - Django admin actions for common tasks
   - Bulk import/export for memberships

4. Performance optimization:
   - Add database query optimization if needed
   - Add select_related/prefetch_related where needed
   - Consider caching if performance issues arise

5. Polish UI:
   - Improve error messages
   - Add helpful tooltips
   - Improve accessibility

6. Create demo video (optional):
   - Requesting access walkthrough
   - Managing projects walkthrough

**Files Created/Modified**:

- `README.md` - Update with new system
- `docs/user_guide_project_access.md` - New guide
- `docs/admin_guide_project_management.md` - New guide
- `docs/project_lead_guide.md` - New guide
- `docs/api_authorization_examples.md` - API examples
- `backend/dataportal/admin.py` - Admin improvements
- Various UI files for polish

**Acceptance Criteria**:

- All documentation complete and accurate
- Guides easy to follow
- Admin tools functional
- Performance acceptable
- UI polished and user-friendly

---

## Rollback Strategy

Each MR is designed to be independently reviewable and deployable with minimal breaking changes until Phase 8.

### Phases 1-7: Low Risk Rollback

- Can be rolled back by reverting the MR
- No user-facing impact
- Database migrations can be reversed

### Phase 8: Critical Transition

- Requires careful planning and communication
- Rollback procedure:
  1. Revert code deployment
  2. Re-enable old authorization checks
  3. Communicate to users
  4. Investigate and fix issues
  5. Re-attempt when ready
- Database changes (project memberships) persist but old system ignores them

### Phase 9: Point of No Return

- Should only be deployed after Phase 8 is stable
- Rollback requires restoring database backup
- Not recommended to rollback after this point

---

## Testing Strategy

### Unit Tests

- Model methods and validation
- Helper functions
- Individual permission checks
- Edge cases and error conditions

### Integration Tests

- Complete workflows:
  - User requests access → Lead approves → User accesses data
  - User requests access → Lead denies → User sees denial
  - User leaves project → User loses access
- Multi-project scenarios
- Authorization checks across all endpoints

### Performance Tests

- Permission check query performance
- Large-scale project membership queries (100+ members)
- Concurrent access request processing
- GraphQL query optimization

### Manual Testing Checklist

- [ ] Anonymous user can view non-embargoed data
- [ ] Anonymous user cannot download
- [ ] Logged-in user without membership can view and download non-embargoed data
- [ ] Logged-in user without membership cannot download embargoed data
- [ ] Project member can view all project data
- [ ] Project member can download project data
- [ ] User can request access to project
- [ ] Lead receives email notification
- [ ] Lead can approve request
- [ ] User receives approval email
- [ ] User gains immediate access after approval
- [ ] Lead can deny request
- [ ] User receives denial email
- [ ] User can withdraw request
- [ ] Manager can add/remove members
- [ ] Manager can promote to manager
- [ ] Manager cannot promote to owner
- [ ] Manager cannot remove owner
- [ ] Owner cannot be removed
- [ ] Superuser has full access to everything

### Frontend Tests

- Component rendering
- User workflows
- Lead workflows
- Form validation
- Error handling
- Accessibility

---

## Security Considerations

1. **Server-Side Authorization**: All authorization checks MUST be server-side. Frontend checks are only for UI/UX.

2. **Prevent Privilege Escalation**:
   - Users cannot make themselves leads
   - Managers cannot promote to owner
   - Owner cannot be removed

3. **SQL Injection Prevention**: Use Django ORM, never raw SQL with user input

4. **Rate Limiting**: Implement rate limiting on:
   - Access request creation (max 5 requests per hour)
   - Email sending

5. **Audit Logging**: Track all permission changes:
   - Who approved requests
   - When memberships were granted/revoked
   - Who performed actions

6. **Input Validation**:
   - Sanitize all user inputs (request messages, notes)
   - Validate email addresses
   - Validate project/user IDs

7. **Email Security**:
   - Use secure SMTP
   - Don't expose email addresses unnecessarily
   - Include unsubscribe options

8. **API Token Security**:
   - Tokens inherit user permissions (no elevation)
   - Token usage logged
   - Expired tokens rejected

---

## Performance Considerations

### Database Optimization

- Add indexes on foreign keys (user, project)
- Add indexes on frequently queried fields (status, role)
- Use `select_related()` for single foreign keys
- Use `prefetch_related()` for reverse foreign keys and many-to-many
- Consider materialized views for complex queries if needed

### Query Optimization Patterns

```python
# Good: Use select_related for project
memberships = user.project_memberships.select_related('project').all()

# Good: Prefetch memberships when querying projects
projects = Project.objects.prefetch_related(
    'memberships__user'
).all()

# Good: Check membership with exists()
has_access = user.project_memberships.filter(project=project).exists()

# Bad: Don't load all memberships just to count
# count = len(user.project_memberships.all())  # NO!
count = user.project_memberships.count()  # YES!
```

### Caching Strategy (If Needed)

- Start without caching, measure performance
- If needed, cache:
  - User's project memberships (short TTL: 5-10 minutes)
  - Project member counts
  - Available projects list
- Cache invalidation:
  - On membership creation/deletion
  - On access request approval
  - On project updates
- Use Django cache framework with Redis backend

### Email Performance

- Send emails asynchronously (consider Celery for production)
- Batch notifications if multiple leads
- Queue emails during request processing

---

## Open Questions & Future Enhancements

### Potential Future Enhancements (Out of Scope)

1. **Membership Expiration**: Auto-expire memberships after X months
2. **Project Visibility**: Public vs Private projects
3. **Role Hierarchy**: Add more granular roles (Contributor, Viewer, etc.)
4. **Approval Workflows**: Require multiple approvals for certain projects
5. **Usage Analytics**: Track data access patterns
6. **Bulk Actions**: Bulk approve/deny requests
7. **Project Templates**: Templates for common project configurations
8. **API Scoped Tokens**: Tokens limited to specific projects
9. **Two-Factor Auth**: For sensitive projects
10. **Data Use Agreements**: Require users to accept terms before access

---

## Summary of Key Decisions

Based on user requirements, the following key decisions were made:

1. **Three Roles**: OWNER (1 per project), MANAGER (multiple), MEMBER (multiple)
2. **Project Owners**: Cannot be removed, assigned at creation
3. **Access Rules**: Project members bypass embargo, non-members see only non-embargoed
4. **Download Restrictions**: Only project members can download embargoed data. Logged in members can download non-embargoed data.
5. **Clean Transition**: All users (including UNRESTRICTED) start with no project access
6. **Email Notifications**: Required for access request workflow
7. **No Caching Initially**: Optimize queries first, add caching only if needed
8. **Superuser Access**: Superusers bypass all restrictions
9. **No Expiration**: Project memberships don't expire (can add later)
10. **Simple UI**: Minimal, focused on core functionality

---

## Timeline Estimate

Assuming 1 developer working full-time:

- **Phase 1**: 3-5 days (models, migrations, admin)
- **Phase 2**: 3-4 days (helper methods, tests)
- **Phase 3**: 5-7 days (GraphQL schema, mutations, tests)
- **Phase 4**: 5-7 days (frontend user UI)
- **Phase 5**: 4-5 days (frontend lead UI)
- **Phase 6**: 3-4 days (email notifications)
- **Phase 7**: 2-3 days (migration script, documentation)
- **Phase 8**: 5-7 days (switch logic, integration tests, deployment)
- **Phase 9**: 2-3 days (cleanup, deprecation)
- **Phase 10**: 3-4 days (documentation, polish)

**Total**: 35-53 days (~7-11 weeks for 1 developer)

With 2 developers working in parallel (backend + frontend), timeline could be reduced to ~4-6 weeks.

---

## Conclusion

This architecture provides a robust, scalable, project-based authorization system while maintaining backward compatibility during transition. The phased approach minimizes risk and allows for incremental review and deployment.

The system is designed to be simple to use (for end users), simple to manage (for project leads), and simple to maintain (for developers), while providing fine-grained access control based on scientific project membership.
