# Pull Request Templates

This directory contains standardized PR templates for different types of changes:

## 📁 Available Templates

### 🆕 [Feature Template](./feature_template.md)
Use for new features, enhancements, and regular development work
- Comprehensive testing checklist
- Security and performance considerations
- Architecture compliance verification
- Mobile and responsive design checks

### 🚨 [Hotfix Template](./hotfix_template.md)  
Use for critical production fixes requiring urgent deployment
- Impact assessment and rollback planning
- Expedited review process
- Post-deployment monitoring plan

### 🚀 [Release Template](./release_template.md)
Use for release preparation and version tagging
- Complete release testing verification
- Deployment and migration planning  
- Performance benchmarking
- Success metrics definition

## 🔄 Template Usage

GitHub will automatically suggest the appropriate template based on your branch naming:
- `feature/*` → Feature Template
- `hotfix/*` → Hotfix Template  
- `release/*` → Release Template

## ✏️ Customizing Templates

Templates can be customized for specific needs while maintaining the core structure:
1. Keep the essential checklists for quality assurance
2. Add project-specific requirements as needed
3. Update labels and assignees for your workflow
4. Maintain consistency with PLANNING.md architecture

## 📋 Review Process

All PR templates include reviewer checklists to ensure:
- Code quality standards are met
- Testing coverage is adequate
- Security considerations are addressed
- Performance impact is acceptable
- Documentation is updated

These templates support the FamilyCart development workflow outlined in `DEVELOPMENT_WORKFLOW_PROPOSAL.md` and follow the branching strategy defined in `.github/copilot-instructions.md`.
