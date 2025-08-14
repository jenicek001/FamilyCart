import LoginForm from '@/components/auth/LoginForm';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Login - FamilyCart',
  description: 'Login to your FamilyCart account.',
};

export default function LoginPage() {
  return <LoginForm />;
}
