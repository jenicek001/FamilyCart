import React, { useState } from 'react';
import axios from 'axios';
import { User } from '@/types';

interface UnverifiedUserAlertProps {
  user: User | null;
  token: string | null;
}

export const UnverifiedUserAlert: React.FC<UnverifiedUserAlertProps> = ({ user, token }) => {
  const [resending, setResending] = useState(false);
  const [resendMessage, setResendMessage] = useState('');

  const handleResendEmail = async () => {
    setResending(true);
    setResendMessage('');
    try {
      let email = '';
      
      // Try to get email from user object first (reliable)
      if (user?.email) {
        email = user.email;
      } 
      // Fallback: try to extract from token (unreliable if token only has sub)
      else {
        try {
          if (token) {
            const parts = token.split('.');
            if (parts.length === 3) {
              // Handle base64url format
              const base64 = parts[1].replace(/-/g, '+').replace(/_/g, '/');
              const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
                  return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
              }).join(''));
              const payload = JSON.parse(jsonPayload);
              email = payload.sub || payload.email; 
            }
          }
        } catch (e) {
          console.error("Failed to decode token", e);
        }
      }

      if (!email) {
         throw new Error("Could not determine email address. Please sign out and sign in again.");
      }

      // Check if email looks like a UUID (which happens if sub is used as email)
      // Simple regex for UUID: 8-4-4-4-12 hex digits
      const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
      if (uuidRegex.test(email)) {
         throw new Error("Cannot verify email: Session contains ID instead of email. Please sign out and sign in again.");
      }

      await axios.post('/api/v1/auth/verify/request-verify-token', 
        { email },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setResendMessage('Verification email sent! Please check your inbox.');
    } catch (error: any) {
      console.error("Resend email error:", error);
      let msg = 'Failed to resend email. Please try again.';
      
      if (error.response?.data?.detail) {
         const detail = error.response.data.detail;
         if (Array.isArray(detail)) {
             // Handle Pydantic validation error
             msg = detail.map((e: any) => `${e.loc.join('.')}: ${e.msg}`).join(', ');
         } else if (typeof detail === 'string') {
             msg = detail;
         } else {
             msg = JSON.stringify(detail);
         }
      } else if (error.message) {
         msg = error.message;
      }
      setResendMessage(msg);
    } finally {
      setResending(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
      <div className="text-center max-w-md mx-auto p-8 bg-white rounded-lg shadow-lg">
        <div className="mb-4">
          <svg className="w-16 h-16 mx-auto text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-slate-900 mb-3">Verify Your Email</h2>
        <p className="text-slate-600 mb-4">
          We've sent a verification email to your inbox. Please check your email and click the verification link to access your shopping lists.
        </p>
        <p className="text-sm text-slate-500 mb-4">
          Didn't receive the email? Check your spam folder.
        </p>
        <button
          onClick={handleResendEmail}
          disabled={resending}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          {resending ? 'Sending...' : 'Resend Verification Email'}
        </button>
        {resendMessage && (
          <p className={`mt-4 text-sm ${resendMessage.includes('sent') ? 'text-green-600' : 'text-red-600'}`}>
            {resendMessage}
          </p>
        )}
      </div>
    </div>
  );
};
