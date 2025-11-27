"use client";

import { Suspense, useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import axios from 'axios';

function VerifyEmailContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');

  useEffect(() => {
    const verifyEmail = async () => {
      const token = searchParams.get('token');
      
      if (!token) {
        setStatus('error');
        setMessage('No verification token provided.');
        return;
      }

      try {
        // Call the backend verification endpoint
        await axios.post(`/api/v1/auth/verify/verify`, { token });
        
        setStatus('success');
        setMessage('Your email has been verified successfully!');
        
        // Redirect after 2 seconds
        setTimeout(() => {
          // Go to login page where user can sign in with their verified account
          router.push('/login?verified=true');
        }, 2000);
      } catch (error: any) {
        // Check if error is "already verified"
        const errorDetail = error.response?.data?.detail || '';
        if (errorDetail.includes('VERIFY_USER_ALREADY_VERIFIED') || errorDetail.includes('already verified')) {
          // User is already verified, treat as success
          setStatus('success');
          setMessage('Your email is already verified!');
          
          setTimeout(() => {
            router.push('/login?verified=true');
          }, 2000);
        } else {
          setStatus('error');
          const errorMessage = error.response?.data?.detail || 'Verification failed. The link may be invalid or expired.';
          setMessage(errorMessage);
        }
      }
    };

    verifyEmail();
  }, [searchParams, router]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
        {status === 'loading' && (
          <>
            <div className="mb-4">
              <svg className="animate-spin h-16 w-16 mx-auto text-blue-600" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-slate-900 mb-2">Verifying your email...</h2>
            <p className="text-slate-600">Please wait while we verify your email address.</p>
          </>
        )}

        {status === 'success' && (
          <>
            <div className="mb-4">
              <svg className="w-16 h-16 mx-auto text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-slate-900 mb-2">Email Verified!</h2>
            <p className="text-slate-600 mb-4">{message}</p>
            <p className="text-sm text-slate-500">Redirecting you to the dashboard...</p>
          </>
        )}

        {status === 'error' && (
          <>
            <div className="mb-4">
              <svg className="w-16 h-16 mx-auto text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-slate-900 mb-2">Verification Failed</h2>
            <p className="text-slate-600 mb-4">{message}</p>
            <button
              onClick={() => router.push('/')}
              className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Go to Home
            </button>
          </>
        )}
      </div>
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
        <div className="text-center">
          <div className="mb-4">
            <svg className="animate-spin h-16 w-16 mx-auto text-blue-600" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
          <p className="text-slate-600">Loading...</p>
        </div>
      </div>
    }>
      <VerifyEmailContent />
    </Suspense>
  );
}
