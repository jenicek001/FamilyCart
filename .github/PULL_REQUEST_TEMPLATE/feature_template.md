---
name: Feature Pull Request
about: Template for feature branch pull requests
title: 'feat: [Brief description]'
labels: ['feature', 'needs-review']
assignees: ''
---

## 🎯 Feature Summary
<!-- Brief description of what this PR implements -->

## 📋 Related Issues
<!-- Link to issues, user stories, or tasks -->
- Closes #
- Related to Sprint: 
- Task in TASKS.md: 

## 🔄 Changes Made
<!-- Detailed list of changes -->
### Backend Changes
- [ ] New API endpoints
- [ ] Database schema changes
- [ ] Business logic updates
- [ ] Configuration changes

### Frontend Changes
- [ ] New components
- [ ] UI/UX improvements
- [ ] State management updates
- [ ] Styling changes

### Documentation
- [ ] README.md updated
- [ ] API documentation updated
- [ ] Code comments added
- [ ] Architecture docs updated

## 🧪 Testing
<!-- Testing approach and coverage -->
### Backend Testing
- [ ] Unit tests added/updated (minimum 3 per feature)
- [ ] Integration tests cover new endpoints
- [ ] PyTest coverage maintained >90%
- [ ] All existing tests pass

### Frontend Testing
- [ ] Component tests added/updated  
- [ ] E2E tests cover user workflows
- [ ] Jest/Playwright tests pass
- [ ] Cross-browser compatibility verified

### Manual Testing
- [ ] Feature tested in development environment
- [ ] UAT environment deployment successful
- [ ] Mobile responsiveness verified
- [ ] Accessibility standards maintained

## 🔒 Security Considerations
- [ ] No sensitive data exposed in logs
- [ ] Input validation implemented
- [ ] Authentication/authorization checked
- [ ] SQL injection prevention verified
- [ ] XSS protection maintained

## 📊 Performance Impact
- [ ] Database query performance analyzed
- [ ] Frontend bundle size impact assessed
- [ ] Memory usage tested
- [ ] No significant performance regression

## 🏗️ Architecture Compliance
- [ ] Follows PLANNING.md patterns
- [ ] Code structure under 500 lines per file
- [ ] Clear separation of concerns
- [ ] Proper error handling implemented
- [ ] Logging added for debugging

## ✅ Code Quality Checklist
### Backend
- [ ] PyLint score >8.0
- [ ] Black formatting applied
- [ ] Isort imports organized
- [ ] Bandit security scan passed
- [ ] Type hints included
- [ ] Docstrings follow Google style

### Frontend
- [ ] ESLint rules passed
- [ ] Prettier formatting applied
- [ ] TypeScript strict mode compliant
- [ ] No `any` types used
- [ ] Component interfaces defined

## 🚀 Deployment Readiness
- [ ] Environment variables documented
- [ ] Database migrations tested
- [ ] Docker builds successfully
- [ ] CI/CD pipeline passes
- [ ] Rollback plan documented

## 📱 Mobile & Responsive Design
- [ ] Mobile viewport tested (375px, 414px)
- [ ] Tablet viewport tested (768px, 1024px)
- [ ] Desktop viewport tested (1920px+)
- [ ] Touch interactions work properly
- [ ] Loading states mobile-friendly

## 🎨 UI/UX Consistency
- [ ] Family Warmth color palette used
- [ ] Typography standards followed
- [ ] Icon library consistency maintained
- [ ] Button styling standardized
- [ ] Error states designed

## 📋 Reviewer Notes
<!-- Any specific areas you'd like reviewers to focus on -->

## 🔄 Post-Merge Tasks
<!-- Tasks to complete after merge -->
- [ ] Update TASKS.md to mark completed
- [ ] Create/update sprint documentation
- [ ] Monitor production metrics
- [ ] Verify UAT environment health

---

## Review Checklist for Reviewers
- [ ] Code follows project architecture patterns
- [ ] All automated checks pass (CI/CD pipeline)
- [ ] Testing coverage is adequate and meaningful
- [ ] Security considerations addressed
- [ ] Performance impact acceptable
- [ ] Documentation updated appropriately
- [ ] Backward compatibility maintained
- [ ] Mobile responsiveness verified
