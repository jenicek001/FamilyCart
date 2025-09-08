---
name: Hotfix Pull Request
about: Template for critical production fixes
title: 'hotfix: [Critical issue description]'
labels: ['hotfix', 'critical', 'needs-urgent-review']
assignees: ''
---

## 🚨 Hotfix Summary
<!-- Brief description of the critical issue and fix -->
**Severity**: [ ] Critical | [ ] High | [ ] Medium
**Production Impact**: <!-- Describe current production impact -->

## 🔥 Issue Details
### Problem Description
<!-- Detailed description of the production issue -->

### Root Cause Analysis
<!-- What caused this issue -->

### Impact Assessment
- **Users Affected**: 
- **Service Downtime**: 
- **Data Impact**: 
- **Business Impact**: 

## 🛠️ Solution Implemented
### Changes Made
<!-- Detailed list of changes -->

### Files Modified
- [ ] Backend files: 
- [ ] Frontend files: 
- [ ] Configuration files: 
- [ ] Database changes: [ ] Yes | [ ] No

## ✅ Verification Steps
### Testing Performed
- [ ] Issue reproduced in development
- [ ] Fix verified in development
- [ ] Regression testing completed
- [ ] Edge cases considered

### Rollback Plan
<!-- How to rollback if this fix causes issues -->

## 🚀 Deployment Strategy
- [ ] Can be deployed immediately
- [ ] Requires maintenance window
- [ ] Requires database migration
- [ ] Requires service restart

### Deployment Order
1. 
2. 
3. 

## 📊 Monitoring Plan
### Metrics to Watch
- [ ] Error rates
- [ ] Response times
- [ ] User activity
- [ ] System resources

### Success Criteria
<!-- How to measure that the fix works -->

## 🔒 Security Impact
- [ ] No new security vulnerabilities introduced
- [ ] Security scan completed
- [ ] No sensitive data exposed

## 📋 Post-Deployment Tasks
- [ ] Monitor production metrics for 2 hours
- [ ] Update incident documentation
- [ ] Schedule post-mortem meeting
- [ ] Update preventive measures

## ⏰ Timeline
- **Issue Discovered**: 
- **Fix Developed**: 
- **Testing Completed**: 
- **Ready for Deployment**: 

---

## Urgent Review Required
This hotfix addresses a critical production issue. Please review and approve as soon as possible.

**Reviewer Checklist**:
- [ ] Fix addresses root cause
- [ ] No additional risks introduced
- [ ] Rollback plan is clear
- [ ] Testing is adequate for urgency level
