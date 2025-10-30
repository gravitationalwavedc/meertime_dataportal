# Authorization System - File Structure

This document shows all files that will be created or modified during the 10-phase implementation.

## Phase 1: Foundation & Models

### New Files
```
backend/dataportal/tests/test_authorization_models.py
backend/dataportal/migrations/XXXX_add_project_authorization.py
```

### Modified Files
```
backend/dataportal/models.py
  - Add ProjectMembership model
  - Add ProjectAccessRequest model
  - Add fields to Project: description, contact_email
  - Add methods to Project: get_owner(), get_leads(), get_all_members()

backend/dataportal/admin.py
  - Register ProjectMembership
  - Register ProjectAccessRequest
  - Add inline admin for Project memberships
```

## Phase 2: Helper Methods & Utilities

### New Files
```
backend/utils/authorization.py
backend/user_manage/tests/test_user_authorization.py
backend/dataportal/tests/test_observation_authorization.py
```

### Modified Files
```
backend/user_manage/models.py
  - Add get_project_memberships()
  - Add can_access_project()
  - Add is_project_lead()
  - Add is_project_owner()
  - Add get_accessible_projects()
  - Add has_any_project_access()
  - Add get_led_projects()

backend/dataportal/models.py
  - Add can_user_access()
  - Add can_user_download()
  - Update is_restricted() to use new logic
```

## Phase 3: GraphQL Schema Updates

### New Files
```
backend/dataportal/graphql/mutations/project_authorization.py
backend/dataportal/graphql/decorators.py
backend/dataportal/graphql/tests/test_project_authorization_graphql.py
```

### Modified Files
```
backend/dataportal/graphql/queries.py
  - Add myProjectMemberships query
  - Add myProjectAccessRequests query
  - Add projectMembers query
  - Add projectAccessRequests query
  - Add availableProjects query

backend/dataportal/graphql/mutations.py
  - Add requestProjectAccess
  - Add withdrawAccessRequest
  - Add approveProjectAccess
  - Add denyProjectAccess
  - Add removeProjectMember
  - Add promoteToManager
  - Add leaveProject
```

## Phase 4: Frontend - User UI

### New Files
```
frontend/src/components/projects/ProjectList.jsx
frontend/src/components/projects/ProjectCard.jsx
frontend/src/components/projects/ProjectAccessRequestButton.jsx
frontend/src/components/projects/MyProjectMemberships.jsx
frontend/src/components/projects/MyAccessRequests.jsx
frontend/src/pages/Projects.jsx
frontend/src/tests/components/projects/ProjectList.test.jsx
frontend/src/tests/components/projects/MyProjectMemberships.test.jsx
frontend/src/__generated__/*.graphql.js (Relay artifacts)
```

### Modified Files
```
frontend/src/pages/Profile.jsx
  - Add "My Projects" section
  - Add "Access Requests" section
  - Add "Leave Project" functionality

frontend/src/App.jsx
  - Add /projects route
```

## Phase 5: Frontend - Lead UI

### New Files
```
frontend/src/components/projects/ProjectManagementDashboard.jsx
frontend/src/components/projects/AccessRequestList.jsx
frontend/src/components/projects/ProjectMemberList.jsx
frontend/src/components/projects/AccessRequestReviewModal.jsx
frontend/src/pages/ProjectManagement.jsx
frontend/src/tests/components/projects/ProjectManagement.test.jsx
```

### Modified Files
```
frontend/src/components/navigation/Navigation.jsx
  - Add link to project management (for leads only)
```

## Phase 6: Email Notifications

### New Files
```
backend/dataportal/notifications.py
backend/dataportal/signals.py
backend/templates/emails/access_request_created.html
backend/templates/emails/access_request_created.txt
backend/templates/emails/access_request_approved.html
backend/templates/emails/access_request_approved.txt
backend/templates/emails/access_request_denied.html
backend/templates/emails/access_request_denied.txt
backend/templates/emails/base_email.html
backend/meertime/settings/email.py
backend/dataportal/tests/test_notifications.py
```

### Modified Files
```
backend/.env.template
  - Add EMAIL_HOST
  - Add EMAIL_PORT
  - Add EMAIL_HOST_USER
  - Add EMAIL_HOST_PASSWORD
  - Add EMAIL_FROM_ADDRESS

backend/meertime/settings/__init__.py
  - Import email settings
```

## Phase 7: Migration Script & Documentation

### New Files
```
backend/user_manage/management/commands/migrate_authorization.py
backend/user_manage/tests/test_migration_command.py
docs/authorization_migration.md
docs/user_communication_template.md
docs/admin_setup_guide.md
docs/faq_project_access.md
```

## Phase 8: Switch Authorization Logic

### Modified Files
```
backend/dataportal/graphql/queries.py
  - Replace @user_passes_test decorators
  - Use @project_member_required or can_user_access()

backend/dataportal/views.py
  - Replace is_restricted() calls
  - Add can_user_download() checks
  - Update error messages

backend/dataportal/graphql/decorators.py
  - Add @project_member_required
  - Add @project_lead_required

frontend/src/**/*.jsx
  - Update components to use new authorization
  - Remove "restricted" field usage
  - Add project membership checks

backend/dataportal/tests/test_authorization_integration.py
  - Comprehensive integration tests
```

## Phase 9: Deprecation & Cleanup

### New Files
```
backend/user_manage/migrations/XXXX_remove_user_role.py
```

### Modified Files
```
backend/user_manage/models.py
  - Remove role field
  - Remove is_unrestricted()

backend/utils/constants.py
  - Update UserRole enum (remove RESTRICTED, UNRESTRICTED)

backend/dataportal/models.py
  - Remove is_restricted()

All test files:
  - Remove old role-based tests
  - Update remaining tests
```

## Phase 10: Documentation & Polish

### New Files
```
docs/user_guide_project_access.md
docs/admin_guide_project_management.md
docs/project_lead_guide.md
docs/api_authorization_examples.md
```

### Modified Files
```
README.md
  - Update with new authorization system
  - Update setup instructions

backend/dataportal/admin.py
  - Add admin actions for common tasks
  - Add bulk operations

Various frontend files:
  - UI polish
  - Improved error messages
  - Accessibility improvements
```

## File Count Summary

| Phase | New Files | Modified Files |
|-------|-----------|----------------|
| 1 | 2 | 2 |
| 2 | 3 | 2 |
| 3 | 3 | 2 |
| 4 | 8+ | 2 |
| 5 | 5+ | 1 |
| 6 | 11 | 2 |
| 7 | 6 | 0 |
| 8 | 1 | 4+ |
| 9 | 1 | 4+ |
| 10 | 4 | 2+ |
| **Total** | **~44** | **~21** |

## Directory Structure

```
meertime_dataportal/
├── backend/
│   ├── dataportal/
│   │   ├── models.py (modified)
│   │   ├── admin.py (modified)
│   │   ├── notifications.py (new)
│   │   ├── signals.py (new)
│   │   ├── graphql/
│   │   │   ├── queries.py (modified)
│   │   │   ├── mutations/
│   │   │   │   └── project_authorization.py (new)
│   │   │   ├── decorators.py (new)
│   │   │   └── tests/
│   │   │       └── test_project_authorization_graphql.py (new)
│   │   ├── migrations/
│   │   │   ├── XXXX_add_project_authorization.py (new)
│   │   └── tests/
│   │       ├── test_authorization_models.py (new)
│   │       ├── test_observation_authorization.py (new)
│   │       └── test_authorization_integration.py (new)
│   ├── user_manage/
│   │   ├── models.py (modified)
│   │   ├── management/
│   │   │   └── commands/
│   │   │       └── migrate_authorization.py (new)
│   │   ├── migrations/
│   │   │   └── XXXX_remove_user_role.py (new)
│   │   └── tests/
│   │       ├── test_user_authorization.py (new)
│   │       └── test_migration_command.py (new)
│   ├── utils/
│   │   └── authorization.py (new)
│   ├── meertime/
│   │   └── settings/
│   │       └── email.py (new)
│   └── templates/
│       └── emails/
│           ├── base_email.html (new)
│           ├── access_request_created.html (new)
│           ├── access_request_created.txt (new)
│           ├── access_request_approved.html (new)
│           ├── access_request_approved.txt (new)
│           ├── access_request_denied.html (new)
│           └── access_request_denied.txt (new)
├── frontend/
│   └── src/
│       ├── components/
│       │   └── projects/
│       │       ├── ProjectList.jsx (new)
│       │       ├── ProjectCard.jsx (new)
│       │       ├── ProjectAccessRequestButton.jsx (new)
│       │       ├── MyProjectMemberships.jsx (new)
│       │       ├── MyAccessRequests.jsx (new)
│       │       ├── ProjectManagementDashboard.jsx (new)
│       │       ├── AccessRequestList.jsx (new)
│       │       ├── ProjectMemberList.jsx (new)
│       │       └── AccessRequestReviewModal.jsx (new)
│       └── pages/
│           ├── Projects.jsx (new)
│           ├── ProjectManagement.jsx (new)
│           └── Profile.jsx (modified)
└── docs/
    ├── authorization_migration.md (new)
    ├── user_communication_template.md (new)
    ├── admin_setup_guide.md (new)
    ├── faq_project_access.md (new)
    ├── user_guide_project_access.md (new)
    ├── admin_guide_project_management.md (new)
    ├── project_lead_guide.md (new)
    └── api_authorization_examples.md (new)
```
