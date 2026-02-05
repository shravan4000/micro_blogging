# Walkthrough - Property Management System (Blog Site)

I have implemented the **Edit/Delete** functionality, **Pagination**, **Login Feedback**, **Session UI**, **UI/UX Enhancements**, **Content Moderation**, **Search**, **Categories**, **Rich Text (Markdown)**, **Image Uploads**, and **User Profiles**.

## Changes

### 1. User Profiles
-   **Profile Page**: Public page `/user/<username>` showing avatar, bio, and user's posts.
-   **Edit Profile**: Users can update their Bio and Profile Picture.
-   **Integration**: Author names in posts and the navbar now link to profiles.

### 2. Image Support
-   **Cover Images**: Each blog post can have a cover image.
-   **Profile Pictures**: Users can upload a custom avatar.
-   **Uploads**: Secure handling of file uploads in `static/uploads`.

### 3. Rich Text (Markdown) Support
-   **Markdown**: Users can write posts in Markdown.
-   **Sanitization**: `bleach` ensures no harmful HTML is rendered.

### 4. Categories & Organization
-   **Tagging**: Blogs effectively tagged with categories.
-   **Filtering**: Easy filtering by category from the home page.

### 5. Search & Discovery
-   **Search**: Find posts by keywords.
-   **Pagination**: Smooth navigation through large sets of posts.

### 6. Moderation & Safety
-   **Automated Moderation**: `alt-profanity-check` filters bad content.
-   **Secure Auth**: Strong password hashing and session management.

## Verification Results

### Automated Checks
- [x] Server runs without errors.
- [x] Database migrations successful (categories, images, profiles).
- [x] All routes (create, edit, delete, profile, search) functional.

### Manual Verification Steps
1.  **User Profile**:
    -   Login and go to "Edit Profile".
    -   Upload a picture and write a bio.
    -   Save and verify the public profile page shows changes.
2.  **Navigation**:
    -   Click "Logged in as [User]" in navbar -> link to profile.
    -   Click author name on a blog card -> link to profile.
