# Kudos System Specification

## Overview

Build an internal web feature that lets employees give kudos to colleagues. A user can choose a colleague, write a short appreciation message, submit it, and see recent kudos in a public dashboard feed. The system must also support administrator moderation so inappropriate, spammy, or duplicate kudos can be hidden or deleted.

## Repository

- Public Git repository: [https://github.com/jeswintom22/datacom-forage.git](https://github.com/jeswintom22/datacom-forage.git)

## Functional Requirements

### User Stories

1. As a user, I can sign in to the internal portal so my kudos are associated with my account.
2. As a user, I can choose a colleague from a searchable list of employees.
3. As a user, I can write and submit a kudos message with clear validation rules.
4. As a user, I can view a public feed of recent kudos on the main dashboard.
5. As a user, I can see only kudos that are visible and not hidden by moderation.
6. As an administrator, I can hide or delete inappropriate kudos messages.
7. As an administrator, I can record a moderation reason when taking action on a kudos.
8. As an administrator, I can review moderation history for accountability.

### Acceptance Criteria

- A user must be authenticated before creating kudos.
- A user can only send kudos to another colleague, not to themselves.
- The kudos message must be required and limited to 500 characters.
- The system must reject empty messages, malformed input, and messages that exceed the length limit.
- The dashboard feed must show the most recent visible kudos first.
- Hidden kudos must not appear in the public feed.
- Deleted kudos must not appear in the public feed and should be recoverable only by admins if soft delete is used.
- Administrators must be able to mark a kudos as hidden or deleted and record why.
- Duplicate submissions and obvious spam should be detectable through validation and moderation workflows.
- The UI must remain usable on desktop and smaller mobile screens.

### Moderation Rules

- Hidden kudos remain in the database but are excluded from the public feed.
- Deleted kudos are treated as removed from normal user views.
- Moderators must provide a reason for moderation action.
- Moderation actions should be audit logged for traceability.
- If a duplicate submission is detected, the system should prevent the second submission or flag it for review.

## Technical Design

### Assumed Architecture

- Frontend: React-based internal portal UI.
- Backend: REST API service.
- Database: PostgreSQL.
- Authentication: Existing corporate SSO or portal session authentication.

### Database Schema

#### users

- `id` (primary key)
- `display_name` (text, required)
- `email` (text, required, unique)
- `role` (text, required; values such as `employee`, `admin`)
- `created_at` (timestamp)
- `updated_at` (timestamp)

#### kudos

- `id` (primary key)
- `sender_id` (foreign key to `users.id`, required)
- `recipient_id` (foreign key to `users.id`, required)
- `message` (text, required, max 500 characters)
- `created_at` (timestamp, required)
- `updated_at` (timestamp)
- `is_visible` (boolean, default `true`)
- `moderated_by` (foreign key to `users.id`, nullable)
- `moderated_at` (timestamp, nullable)
- `reason_for_moderation` (text, nullable)
- `deleted_at` (timestamp, nullable; used if deletion is soft delete)

#### kudos_moderation_audit

- `id` (primary key)
- `kudos_id` (foreign key to `kudos.id`, required)
- `action` (text, required; values such as `hide`, `delete`, `restore`)
- `moderated_by` (foreign key to `users.id`, required)
- `reason` (text, required)
- `created_at` (timestamp, required)

#### Suggested Relationships

- One user can send many kudos.
- One user can receive many kudos.
- One admin can moderate many kudos.
- Each moderation action should be recorded in the audit table.

### API Endpoints

#### Authentication

- `GET /api/me` returns the current signed-in user and role.

#### Colleague Lookup

- `GET /api/users?query=` returns searchable colleagues for the recipient picker.

#### Kudos Creation

- `POST /api/kudos`
- Request body: `recipient_id`, `message`
- Validation: authenticated sender, recipient exists, recipient is not the sender, message length <= 500, duplicate/spam checks.
- Response: created kudos object if accepted, or validation errors if rejected.

#### Kudos Feed

- `GET /api/kudos?visible=true&limit=&cursor=` returns recent visible kudos for the dashboard feed.
- The default feed should exclude hidden and deleted items.

#### Moderation

- `PATCH /api/admin/kudos/:id/hide`
- `PATCH /api/admin/kudos/:id/delete`
- `PATCH /api/admin/kudos/:id/restore`
- Request body: `reason`
- Authorization: admin only.

#### Moderation Audit

- `GET /api/admin/kudos/:id/audit` returns the moderation history for a specific kudos item.

### Frontend Components

- `KudosComposeForm`: lets a user select a colleague, enter a message, and submit.
- `ColleagueSelector`: searchable dropdown or autocomplete list.
- `KudosFeed`: shows recent visible kudos on the dashboard.
- `KudosCard`: displays sender, recipient, message, and timestamp.
- `AdminModerationPanel`: allows admins to hide, delete, restore, and view reasons.
- `ModerationReasonDialog`: captures a required reason before moderation is saved.

### Security Considerations

- Enforce authentication for creation and moderation actions.
- Enforce authorization so only admins can moderate.
- Sanitize all message and reason inputs before storage and rendering.
- Prevent users from submitting kudos to themselves.
- Rate limit kudos creation to reduce spam.
- Add duplicate detection using sender, recipient, message fingerprinting, and a short time window.
- Use parameterized queries and server-side validation.

### Performance Considerations

- Paginate the kudos feed.
- Index `created_at`, `recipient_id`, `sender_id`, and `is_visible`.
- Cache the public feed briefly if traffic grows.
- Use cursor-based pagination for stable feed ordering.

### Error Handling and Logging

- Return structured validation errors for invalid kudos submissions.
- Log moderation actions with actor, target kudos ID, action, and reason.
- Log rejected spam or duplicate submissions for operational review.
- Avoid exposing internal stack traces to end users.

## Implementation Plan

1. Define database migrations for `users`, `kudos`, and `kudos_moderation_audit`.
2. Implement authentication and role-based authorization.
3. Build colleague lookup and kudos creation endpoints with validation.
4. Add feed retrieval with visibility filtering and pagination.
5. Implement admin moderation actions and audit logging.
6. Build the compose form, feed, and admin moderation UI components.
7. Add duplicate/spam detection and hidden/deleted visibility rules.
8. Add automated tests for validation, moderation, and feed visibility.
9. Perform end-to-end testing on desktop and mobile layouts.
10. Prepare deployment settings, database migration steps, and logging configuration.

## Out Of Scope For Initial Release

- Reactions, comments, or threaded conversations.
- File attachments or image uploads.
- Advanced ML-based toxicity detection.
- Notification email or chat delivery for kudos.
