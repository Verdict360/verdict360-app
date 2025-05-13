#!/bin/bash

# This is a script to document the manual steps for setting up a project board
# You would typically run these commands using the GitHub CLI or API

# Create a project board
# gh project create Verdict360 --org Verdict360

echo "Project Board Setup Instructions:"
echo "================================"
echo "1. Create a new project board named 'Verdict360 Development'"
echo "2. Add the following columns:"
echo "   - Backlog"
echo "   - To Do"
echo "   - In Progress"
echo "   - Legal Review"
echo "   - QA Testing"
echo "   - Done"
echo ""
echo "3. Add the following labels to the repository:"
echo "   - workflow:legal-review-required"
echo "   - workflow:popia-compliance"
echo "   - legal:citation-system"
echo "   - legal:south-african-context"
echo "   - legal:document-processing"
echo "   - legal:audio-recording"
echo "   - type:bug"
echo "   - type:feature"
echo "   - type:legal-document"
echo "   - type:export-template"
echo ""
echo "4. Set up automation rules:"
echo "   - When issues with 'workflow:legal-review-required' are added, move to Legal Review column"
echo "   - When PRs are approved, move to QA Testing column"
echo "   - When PRs are merged, move to Done column"
