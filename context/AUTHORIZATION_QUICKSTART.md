# Authorization System Implementation - Quick Reference

## Document Overview

I've created a comprehensive **authorization_architecture.md** document (1,157 lines) that provides a complete blueprint for implementing the new project-based authorization system for the MeerTime Data Portal.

## What's in the Document

### 1. Architecture Details

- **Three membership roles**: OWNER (primary lead), MANAGER (can manage members), MEMBER (has access)
- **Authorization rules**: Clear hierarchy from superusers to anonymous users
- **Complete model definitions**: ProjectMembership and ProjectAccessRequest with all fields and methods
- **Access request workflow**: Step-by-step process from request to approval

### 2. Implementation Plan (10 Phases)

Each phase is a separate MR designed for easy review:

| Phase | Name                       | Duration | Breaking Changes |
| ----- | -------------------------- | -------- | ---------------- |
| 1     | Foundation & Models        | 3-5 days | No               |
| 2     | Helper Methods & Utilities | 3-4 days | No               |
| 3     | GraphQL Schema Updates     | 5-7 days | No               |
| 4     | Frontend - User UI         | 5-7 days | No               |
| 5     | Frontend - Lead UI         | 4-5 days | No               |
| 6     | Email Notifications        | 3-4 days | No               |
| 7     | Migration Script & Docs    | 2-3 days | No               |
| 8     | Switch Authorization Logic | 5-7 days | **YES**          |
| 9     | Deprecation & Cleanup      | 2-3 days | **YES**          |
| 10    | Documentation & Polish     | 3-4 days | No               |

**Total estimated time**: 35-53 days (7-11 weeks for 1 developer, 4-6 weeks for 2)

### 3. Key Decisions Incorporated

✅ **Use existing Project model** - No new models for projects themselves
✅ **Three roles**: OWNER (unique, unremovable), MANAGER, MEMBER
✅ **Project metadata**: Added `description` and `contact_email` to Project model
✅ **Clean transition**: ALL users (including UNRESTRICTED) start with no access, must request
✅ **Email notifications**: Required for workflow (Phase 6)
✅ **No caching initially**: Optimize queries first, add caching only if needed
✅ **Download restrictions**: Only project members can download data that isn't embargoed. Anyone logged in can download non-embargoed data.
✅ **Anonymous users**: Can view non-embargoed data, cannot download or request access

### 4. Additional Sections

- **Rollback strategy** for each phase
- **Testing strategy** (unit, integration, performance, manual)
- **Security considerations** (privilege escalation prevention, rate limiting, audit logging)
- **Performance optimization** patterns and tips
- **Future enhancements** (out of scope for initial implementation)

## Next Steps

### Immediate Actions

1. ✅ Review the architecture document
2. Clarify any remaining questions (if needed)
3. Begin Phase 1 implementation

### Phase 1 Kickoff Checklist

When you're ready to start Phase 1:

- [ ] Set up a feature branch (e.g., `feature/authorization-phase1`)
- [ ] Review the Phase 1 tasks in detail
- [ ] Ensure test database is available
- [ ] Begin implementation following the documented tasks

## Quick Reference - Model Definitions

### ProjectMembership

```python
# Three roles: OWNER, MANAGER, MEMBER
# Fields: user, project, role, joined_at, approved_by
# Constraints: One owner per project, unique (user, project)
```

### ProjectAccessRequest

```python
# Four statuses: PENDING, APPROVED, DENIED, WITHDRAWN
# Fields: user, project, status, requested_at, reviewed_at, reviewed_by, message, review_notes
# Constraints: One pending request per (user, project)
```

### Project (Extended)

```python
# New fields: description, contact_email
# New methods: get_owner(), get_leads(), get_all_members()
```

### User (Extended)

```python
# New methods: can_access_project(), is_project_lead(), is_project_owner()
# Old role field kept during transition
```

### Observation (Extended)

```python
# New methods: can_user_access(), can_user_download()
# Old is_restricted() kept as deprecated wrapper
```

## Authorization Flow

```
┌──────────────┐
│ Anonymous    │ → Can VIEW non-embargoed data only
│ User         │ → Cannot DOWNLOAD
└──────────────┘

┌──────────────┐
│ Logged-in    │ → Can VIEW non-embargoed data
│ User         │ → Can DOWNLOAD non-embargoed data
│ (no project) │ → Can REQUEST access
└──────────────┘

┌──────────────┐
│ Project      │ → Can VIEW all project data (including embargoed)
│ MEMBER       │ → Can DOWNLOAD project data
│              │ → Can LEAVE project
└──────────────┘

┌──────────────┐
│ Project      │ → All MEMBER permissions +
│ MANAGER      │ → Can APPROVE/DENY access requests
│              │ → Can ADD/REMOVE members
│              │ → Can PROMOTE to MANAGER
└──────────────┘

┌──────────────┐
│ Project      │ → All MANAGER permissions +
│ OWNER        │ → Cannot be removed
│              │ → Assigned at project creation
└──────────────┘

┌──────────────┐
│ Superuser    │ → Can access EVERYTHING
│              │ → Can manage ALL projects
└──────────────┘
```

## Critical Phase 8 Notes

Phase 8 is the critical transition where we switch from old to new authorization:

### Pre-Deployment Requirements

- All previous phases deployed and stable
- User communication sent (1 week notice)
- Project owners assigned for all projects
- Rollback procedure tested
- Monitoring in place

### What Happens

- ALL users lose global "unrestricted" access
- Users must request access to specific projects
- Project members get immediate access to all project data
- Anonymous users still see non-embargoed data

### Risk Mitigation

- Deploy to staging first
- Test thoroughly with real data
- Be ready to rollback
- Monitor closely for 24-48 hours after deployment

## Questions or Concerns?

If anything is unclear or you need modifications to the architecture:

1. Ask for clarification
2. I can update the document
3. I can create detailed task breakdowns for any phase

## Ready to Start?

When you're ready to begin Phase 1, let me know and I can:

- Create the initial models code
- Set up the test structure
- Help with any specific implementation details
