"use client";

import type React from 'react';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import axios from 'axios';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { Eye, EyeOff, Mail, Lock, ShoppingCart } from 'lucide-react';
import { LogoWithText } from '@/components/ui/Logo';

export default function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const router = useRouter();
  const { toast } = useToast();
  const { login } = useAuth();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const params = new URLSearchParams();
      params.append('username', email);
      params.append('password', password);

      const { data } = await axios.post('/api/v1/auth/jwt/login', params, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      login(data.access_token);
      toast({
        title: "Login Successful",
        description: "Welcome back!",
      });
      router.push('/dashboard'); // Redirect to dashboard after successful login
    } catch (error: any) {
      toast({
        title: "Login Failed",
        description: error.response?.data?.detail || "Please check your credentials and try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4" style={{
      background: 'linear-gradient(135deg, #fef7ed 0%, #dbeafe 50%, #f0fdf4 100%)'
    }}>
      <Card className="w-full max-w-md shadow-2xl border-0" style={{
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(10px)'
      }}>
        {/* Header with Logo */}
        <CardHeader className="text-center pb-2">
          <div className="flex justify-center mb-4">
            <LogoWithText variant="cart-family" size="lg" />
          </div>
          <CardTitle className="font-headline text-3xl" style={{ color: '#0f172a' }}>
            Welcome Back!
          </CardTitle>
          <CardDescription style={{ color: '#64748b' }}>
            Sign in to access your family shopping lists
          </CardDescription>
        </CardHeader>
        
        <CardContent className="px-6">
          <form onSubmit={handleLogin} className="space-y-6">
            {/* Email Field */}
            <div className="space-y-2">
              <Label htmlFor="email" className="font-medium" style={{ color: '#374151' }}>
                Email
              </Label>
              <div className="relative group">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 transition-colors" 
                     style={{ color: '#9ca3af' }} />
                <Input
                  id="email"
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="pl-10 h-11 transition-all duration-200"
                  style={{
                    borderColor: '#e2e8f0',
                    backgroundColor: '#ffffff'
                  }}
                  onFocus={(e) => {
                    e.target.style.borderColor = '#f59e0b';
                    e.target.style.boxShadow = '0 0 0 3px rgba(245, 158, 11, 0.1)';
                  }}
                  onBlur={(e) => {
                    e.target.style.borderColor = '#e2e8f0';
                    e.target.style.boxShadow = 'none';
                  }}
                />
              </div>
            </div>
            
            {/* Password Field */}
            <div className="space-y-2">
              <Label htmlFor="password" className="font-medium" style={{ color: '#374151' }}>
                Password
              </Label>
              <div className="relative group">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 transition-colors" 
                     style={{ color: '#9ca3af' }} />
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="pl-10 pr-10 h-11 transition-all duration-200"
                  style={{
                    borderColor: '#e2e8f0',
                    backgroundColor: '#ffffff'
                  }}
                  onFocus={(e) => {
                    e.target.style.borderColor = '#f59e0b';
                    e.target.style.boxShadow = '0 0 0 3px rgba(245, 158, 11, 0.1)';
                  }}
                  onBlur={(e) => {
                    e.target.style.borderColor = '#e2e8f0';
                    e.target.style.boxShadow = 'none';
                  }}
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="absolute right-1 top-1/2 -translate-y-1/2 h-8 w-8 hover:bg-gray-100"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  <span className="sr-only">{showPassword ? "Hide password" : "Show password"}</span>
                </Button>
              </div>
            </div>
            
            {/* Login Button */}
            <Button 
              type="submit" 
              className="w-full h-11 font-medium text-base transition-all duration-200 shadow-md hover:shadow-lg"
              disabled={isLoading}
              style={{
                backgroundColor: '#f59e0b',
                color: '#ffffff',
                border: 'none'
              }}
              onMouseEnter={(e) => {
                if (!isLoading) {
                  e.currentTarget.style.backgroundColor = '#d97706';
                }
              }}
              onMouseLeave={(e) => {
                if (!isLoading) {
                  e.currentTarget.style.backgroundColor = '#f59e0b';
                }
              }}
            >
              {isLoading ? (
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Signing in...
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <ShoppingCart className="h-4 w-4" />
                  Sign In
                </div>
              )}
            </Button>
          </form>
        </CardContent>
        
        <CardFooter className="flex flex-col items-center space-y-3 px-6 pb-6">
          <p className="text-sm" style={{ color: '#64748b' }}>
            Don&apos;t have an account?{' '}
            <a href="/signup" className="font-medium underline transition-colors" 
               style={{ color: '#f59e0b' }}
               onMouseEnter={(e) => e.currentTarget.style.color = '#d97706'}
               onMouseLeave={(e) => e.currentTarget.style.color = '#f59e0b'}>
              Create one here
            </a>
          </p>
          <a href="#" className="text-sm font-medium underline transition-colors" 
             style={{ color: '#3b82f6' }}
             onMouseEnter={(e) => e.currentTarget.style.color = '#2563eb'}
             onMouseLeave={(e) => e.currentTarget.style.color = '#3b82f6'}>
            Forgot your password?
          </a>
        </CardFooter>
      </Card>
    </div>
  );
}
