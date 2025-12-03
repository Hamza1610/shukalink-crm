# Admin Router Features

## Overview
The admin router provides comprehensive administrative functionality for the AgriConnect platform. It includes endpoints for user management, platform statistics, content moderation, and system monitoring.

## Authentication & Authorization
- All endpoints require admin authentication using the `require_admin` dependency
- Automatically validates that the current user has `UserType.ADMIN` status
- Returns 403 Forbidden for non-admin users

## User Management
- **GET /users**: Retrieve all users with pagination support
- **GET /users/{user_id}**: Get a specific user by ID
- **PUT /users/{user_id}/user-type**: Update a user's type (farmer, buyer, admin, aggregator)
- **DELETE /users/{user_id}**: Remove a user from the platform

## Platform Analytics
- **GET /statistics**: Get comprehensive platform statistics including:
  - Total users by type (farmers, buyers, admins, aggregators)
  - Total produce listings
  - Total transactions
  - Total notifications
  - Total conversations

## Content & Data Management
- **GET /transactions**: View all platform transactions
- **GET /produce-listings**: View all produce listings
- **GET /logistics-requests**: View all logistics requests
- **PUT /logistics-requests/{request_id}/status**: Update logistics request status

## Notification System
- **GET /notifications**: Retrieve all notifications
- **POST /notifications/broadcast**: Send broadcast notifications to all users or specific user types

## Monitoring & Reporting
- **GET /activity-logs**: Get platform activity metrics for a specified number of days
- Provides user activity, produce activity, and transaction activity statistics

## Error Handling
- Proper HTTP status codes (403, 404, 400) for various error conditions
- Descriptive error messages for debugging
- Input validation for all parameters

## Security Features
- Admin-only access to sensitive operations
- Input validation to prevent invalid data
- Proper session handling through dependency injection

## Use Cases
1. **Platform Monitoring**: Admins can monitor platform health and user activity
2. **User Management**: Manage user accounts and permissions
3. **Content Moderation**: Review and manage listings, transactions, and logistics
4. **Communication**: Send important announcements to users
5. **Data Analysis**: Access platform metrics for business intelligence