# Dark/Light Theme Toggle Implementation

## Overview
A fully functional dark/light theme toggle has been implemented on the shell page that affects all elements throughout the application.

## Features Implemented

### 1. **Theme Toggle Button**
- Added a sun/moon icon toggle button in the navbar (next to the user profile button)
- Icons change based on the current theme:
  - **Sun icon** shown in dark mode (click to switch to light)
  - **Moon icon** shown in light mode (click to switch to dark)

### 2. **CSS Theme Variables**
The following CSS variables were created to handle theming:

**Dark Theme (Default):**
- Background Primary: `#1f2937` (gray-800)
- Background Secondary: `#374151` (gray-700)
- Hover Background: `#4b5563` (gray-600)
- Text Primary: `#ffffff` (white)
- Text Secondary: `#d1d5db` (gray-300)
- Text Muted: `#9ca3af` (gray-400)
- Border Color: `#4b5563` (gray-600)

**Light Theme:**
- Background Primary: `#ffffff` (white)
- Background Secondary: `#f3f4f6` (gray-100)
- Hover Background: `#e5e7eb` (gray-200)
- Text Primary: `#111827` (gray-900)
- Text Secondary: `#374151` (gray-700)
- Text Muted: `#6b7280` (gray-500)
- Border Color: `#d1d5db` (gray-300)

### 3. **Theme Classes**
Custom theme-aware CSS classes were created:
- `.theme-bg-primary` - Main background color
- `.theme-bg-secondary` - Secondary background (navbar, sidebar)
- `.theme-bg-hover` - Hover state background
- `.theme-text-primary` - Primary text color
- `.theme-text-secondary` - Secondary text color
- `.theme-text-muted` - Muted text color
- `.theme-border` - Border color

### 4. **Elements Updated**
All major UI elements now respond to theme changes:
- ✅ Body background
- ✅ Navigation bar
- ✅ Sidebar
- ✅ Sidebar links and icons
- ✅ Search input
- ✅ Buttons and interactive elements
- ✅ Text colors (primary, secondary, muted)
- ✅ Border colors
- ✅ Hover states

### 5. **Persistence**
- Theme preference is saved to `localStorage`
- Theme persists across page refreshes and navigation
- Default theme is **dark mode**

### 6. **Smooth Transitions**
- All theme changes include smooth CSS transitions (0.3s ease)
- No jarring color switches

## How It Works

1. **On Page Load:**
   - Script checks `localStorage` for saved theme preference
   - Applies theme immediately (before page renders to avoid flash)
   - Shows appropriate icon in toggle button

2. **On Toggle Click:**
   - Switches between 'light' and 'dark' themes
   - Updates `data-theme` attribute on `<html>` element
   - Saves preference to `localStorage`
   - Updates toggle button icon

3. **CSS Variables:**
   - All colors reference CSS variables
   - Variables change based on `data-theme` attribute
   - Automatic cascading to all elements using theme classes

## Usage

The theme toggle button is located in the top navigation bar, to the left of the user profile icon. Simply click it to switch between light and dark themes.

## Technical Details

- **Storage:** Browser's localStorage API
- **State Management:** HTML data attribute (`data-theme`)
- **Styling:** CSS custom properties (variables)
- **Icons:** SVG icons from Flowbite/Heroicons
- **Framework:** Tailwind CSS with custom CSS variables

## Browser Compatibility

This implementation works in all modern browsers that support:
- CSS Custom Properties (CSS Variables)
- localStorage API
- ES6 JavaScript

Compatible with: Chrome, Firefox, Safari, Edge (latest versions)
