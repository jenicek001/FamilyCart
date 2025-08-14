"use client";

import type React from 'react';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { Mail, User, Eye, EyeOff, ShoppingCart, Users } from 'lucide-react';
import { LogoWithText } from '@/components/ui/Logo';

export default function SignupPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [nickname, setNickname] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const router = useRouter();
  const { toast } = useToast();
  const { login } = useAuth();

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      toast({
        title: "Passwords do not match",
        variant: "destructive",
      });
      return;
    }
    if (!nickname.trim()) {
      toast({
        title: "Nickname is required",
        variant: "destructive",
      });
      return;
    }
    setIsLoading(true);
    try {
      // Split fullName into first_name and last_name
      const nameParts = fullName.trim().split(' ');
      const firstName = nameParts[0];
      const lastName = nameParts.length > 1 ? nameParts.slice(1).join(' ') : '';
      
      await axios.post('/api/v1/auth/register', {
        email,
        password,
        first_name: firstName,
        last_name: lastName,
        nickname: nickname.trim(),
      });

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
        title: "Signup Successful",
        description: "Welcome to FamilyCart! Redirecting to dashboard...",
      });
    } catch (error: any) {
      toast({
        title: "Signup Failed",
        description: error.response?.data?.detail || "An error occurred. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-8" style={{
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
            Join FamilyCart
          </CardTitle>
          <CardDescription style={{ color: '#64748b' }}>
            Start organizing your family shopping together
          </CardDescription>
        </CardHeader>
        
        <CardContent className="px-6">
          <form onSubmit={handleSignup} className="space-y-5">
            {/* Full Name Field */}
            <div className="space-y-2">
              <Label htmlFor="fullName" className="font-medium" style={{ color: '#374151' }}>
                Full Name
              </Label>
              <div className="relative group">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 transition-colors" 
                     style={{ color: '#9ca3af' }} />
                <Input
                  id="fullName"
                  type="text"
                  placeholder="Your Name"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
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
            
            {/* Nickname Field */}
            <div className="space-y-2">
              <Label htmlFor="nickname" className="font-medium" style={{ color: '#374151' }}>
                Nickname
              </Label>
              <div className="relative group">
                <Users className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 transition-colors" 
                      style={{ color: '#9ca3af' }} />
                <Input
                  id="nickname"
                  type="text"
                  placeholder="How should family call you?"
                  value={nickname}
                  onChange={(e) => setNickname(e.target.value)}
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
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="•••••••• (min. 6 characters)"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="pr-10 h-11 transition-all duration-200"
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
            
            {/* Confirm Password Field */}
            <div className="space-y-2">
              <Label htmlFor="confirmPassword" className="font-medium" style={{ color: '#374151' }}>
                Confirm Password
              </Label>
              <div className="relative group">
                <Input
                  id="confirmPassword"
                  type={showConfirmPassword ? "text" : "password"}
                  placeholder="••••••••"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  className="pr-10 h-11 transition-all duration-200"
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
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                >
                  {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  <span className="sr-only">{showConfirmPassword ? "Hide confirm password" : "Show confirm password"}</span>
                </Button>
              </div>
            </div>
            
            {/* Sign Up Button */}
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
                  Creating Account...
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <Users className="h-4 w-4" />
                  Create Account
                </div>
              )}
            </Button>
          </form>
        </CardContent>
        
        <CardFooter className="flex justify-center px-6 pb-6">
          <p className="text-sm" style={{ color: '#64748b' }}>
            Already have an account?{' '}
            <a href="/login" className="font-medium underline transition-colors" 
               style={{ color: '#f59e0b' }}
               onMouseEnter={(e) => e.currentTarget.style.color = '#d97706'}
               onMouseLeave={(e) => e.currentTarget.style.color = '#f59e0b'}>
              Sign in here
            </a>
          </p>
        </CardFooter>
      </Card>
    </div>
  );
}
