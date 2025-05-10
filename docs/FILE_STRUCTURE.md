# Verdict360 Project File Structure

## Overview

The Verdict360 project follows a monorepo structure with the following main directories:

- `/web`: Next.js web application frontend
- `/api`: Node.js backend API
- `/mobile`: Expo mobile application
- `/docker`: Docker configuration files

## Component Details

### Web Component

The web component is built with Next.js and contains:
- React components for the legal UI
- Authentication integration with Keycloak
- Legal document visualization

### API Component

The API component provides:
- REST endpoints for legal data
- Document processing
- Authentication validation
- Vector search functionality

### Mobile Component

The mobile component includes:
- Audio recording for legal proceedings
- Offline document access
- Mobile-specific authentication
