# Auto-Merge Setup

This repository is configured with GitHub Actions to automatically merge pull requests when certain conditions are met.

## How to Use Auto-Merge

### Option 1: Using the `automerge` Label

1. Create a pull request
2. Add the `automerge` label to the PR
3. Once all required checks pass and approvals are received, the PR will automatically merge

The workflow will:
- Monitor PRs with the `automerge` label
- Enable GitHub's auto-merge feature when the label is added
- Disable auto-merge if the label is removed
- Use squash merge by default

### Option 2: Manual Auto-Merge

You can also enable auto-merge manually:
1. Open your pull request
2. Click "Enable auto-merge" button (if available)
3. Select your preferred merge method
4. The PR will merge automatically when all conditions are met

## Requirements

For auto-merge to work, the following conditions must be met:
- All required status checks must pass
- All required reviews must be approved
- The PR must not be in draft mode
- Branch protection rules must be satisfied

## Repository Settings

To enable auto-merge functionality in your repository:
1. Go to **Settings** → **General** → **Pull Requests**
2. Check **"Allow auto-merge"**
3. Configure branch protection rules for your main branch

## Customization

The auto-merge workflow is configured in `.github/workflows/auto-merge.yml`. You can customize:
- Merge method (squash, merge, rebase)
- Label name
- Additional conditions or checks

## Security Note

Auto-merge should only be used for trusted contributors. Always ensure proper branch protection rules and required reviews are in place.
