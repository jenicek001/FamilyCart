"use client";

import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@/contexts/AuthContext';
import apiClient from '@/lib/api';
import { ShoppingList, User } from '@/types';
import { UserBadge } from '@/components/ui/UserBadge';
import { Share, UserMinus, Crown, Mail, Copy, Check } from 'lucide-react';

interface ShareDialogProps {
  isOpen: boolean;
  onClose: () => void;
  list: ShoppingList;
  onListUpdate?: (updatedList: ShoppingList) => void;
}

export function ShareDialog({ isOpen, onClose, list, onListUpdate }: ShareDialogProps) {
  const [email, setEmail] = useState('');
  const [isInviting, setIsInviting] = useState(false);
  const [isRemoving, setIsRemoving] = useState<string | null>(null);
  const [shareUrlCopied, setShareUrlCopied] = useState(false);
  const { toast } = useToast();
  const { user } = useAuth();

  // Generate a shareable URL (could be enhanced with actual sharing tokens in the future)
  const shareUrl = `${window.location.origin}/dashboard?list=${list.id}`;

  const handleInviteByEmail = async () => {
    if (!email.trim()) {
      toast({
        title: "Email required",
        description: "Please enter an email address to invite.",
        variant: "destructive"
      });
      return;
    }

    if (!email.includes('@')) {
      toast({
        title: "Invalid email",
        description: "Please enter a valid email address.",
        variant: "destructive"
      });
      return;
    }

    setIsInviting(true);
    try {
      const response = await apiClient.post(`/api/v1/shopping-lists/${list.id}/share`, {
        email: email.trim()
      });

      // Update the list with new member if the backend returns it
      if (response.data && onListUpdate) {
        onListUpdate(response.data);
      }

      toast({
        title: "Invitation sent!",
        description: `An invitation has been sent to ${email}. They will get access to "${list.name}" when they create an account or sign in.`
      });
      setEmail('');
    } catch (error: any) {
      console.error('Error sharing list:', error);
      
      // Handle specific error cases
      if (error.response?.status === 403) {
        toast({
          title: "Permission denied",
          description: "Only the list owner can invite new members.",
          variant: "destructive"
        });
      } else if (error.response?.status === 500) {
        toast({
          title: "Failed to send invitation",
          description: "Could not send invitation email. Please check the email address and try again.",
          variant: "destructive"
        });
      } else {
        toast({
          title: "Failed to send invitation",
          description: error.response?.data?.detail || "Could not invite user. Please try again.",
          variant: "destructive"
        });
      }
    } finally {
      setIsInviting(false);
    }
  };

  const handleRemoveMember = async (memberId: string) => {
    if (memberId === user?.id) {
      toast({
        title: "Cannot remove yourself",
        description: "You cannot remove yourself from the list.",
        variant: "destructive"
      });
      return;
    }

    setIsRemoving(memberId);
    try {
      const response = await apiClient.delete(`/api/v1/shopping-lists/${list.id}/members/${memberId}`);
      
      // Update the list with removed member if the backend returns it
      if (response.data && onListUpdate) {
        onListUpdate(response.data);
      }

      toast({
        title: "Member removed",
        description: "The member has been removed from the list."
      });
    } catch (error: any) {
      console.error('Error removing member:', error);
      toast({
        title: "Failed to remove member",
        description: error.response?.data?.detail || "Could not remove member. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsRemoving(null);
    }
  };

  const handleCopyShareUrl = async () => {
    try {
      await navigator.clipboard.writeText(shareUrl);
      setShareUrlCopied(true);
      toast({
        title: "Link copied!",
        description: "The share link has been copied to your clipboard."
      });
      
      // Reset copied state after 2 seconds
      setTimeout(() => setShareUrlCopied(false), 2000);
    } catch (error) {
      toast({
        title: "Failed to copy",
        description: "Could not copy the link. Please copy it manually.",
        variant: "destructive"
      });
    }
  };

  const isOwner = list.owner_id === user?.id;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-md mx-4 sm:mx-0 p-4 sm:p-6 shadow-2xl rounded-xl border-0" style={{
        backgroundColor: 'rgba(255, 255, 255, 0.98)',
        backdropFilter: 'blur(10px)'
      }}>
        <DialogHeader className="pb-2 sm:pb-4" style={{ borderBottomColor: '#f1f5f9' }}>
          <DialogTitle className="flex items-center gap-3 text-lg sm:text-xl" style={{ color: '#0f172a' }}>
            <div className="p-2 rounded-lg" style={{ backgroundColor: 'rgba(245, 158, 11, 0.1)' }}>
              <Share className="h-5 w-5" style={{ color: '#f59e0b' }} />
            </div>
            Share "{list.name}"
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Current Members */}
          <div className="p-4 rounded-xl border" style={{ 
            backgroundColor: '#fef7ed', 
            borderColor: '#fed7aa' 
          }}>
            <h4 className="text-sm font-semibold mb-3 flex items-center gap-2" style={{ color: '#0f172a' }}>
              <Crown className="h-4 w-4" style={{ color: '#f59e0b' }} />
              Family Members ({(list.members?.length || 0) + 1})
            </h4>
            <div className="space-y-3">
              {/* Owner */}
              <div className="flex items-center justify-between p-3 rounded-lg shadow-sm border" style={{
                backgroundColor: '#ffffff',
                borderColor: '#e2e8f0'
              }}>
                <div className="flex items-center gap-3">
                  {isOwner && user ? (
                    <UserBadge user={user} size="sm" showName />
                  ) : (
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-full flex items-center justify-center" style={{
                        backgroundColor: 'rgba(245, 158, 11, 0.2)'
                      }}>
                        <span className="text-sm font-medium" style={{ color: '#f59e0b' }}>?</span>
                      </div>
                      <div>
                        <span className="text-sm font-medium" style={{ color: '#0f172a' }}>Owner</span>
                      </div>
                    </div>
                  )}
                  <Crown className="h-4 w-4" style={{ color: '#f59e0b' }} />
                </div>
                <span className="text-xs font-medium px-2 py-1 rounded-full" style={{
                  color: '#92400e',
                  backgroundColor: '#fef3c7'
                }}>Owner</span>
              </div>
              
              {/* Members */}
              {list.members?.map((member) => (
                <div key={member.id} className="flex items-center justify-between p-3 rounded-lg shadow-sm border" style={{
                  backgroundColor: '#ffffff',
                  borderColor: '#e2e8f0'
                }}>
                  <UserBadge user={member} size="sm" showName />
                  {isOwner && member.id !== user?.id && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleRemoveMember(member.id)}
                      disabled={isRemoving === member.id}
                      className="transition-colors hover:bg-red-50"
                      style={{ color: '#dc2626' }}
                      onMouseEnter={(e) => e.currentTarget.style.color = '#b91c1c'}
                      onMouseLeave={(e) => e.currentTarget.style.color = '#dc2626'}
                    >
                      {isRemoving === member.id ? (
                        <div className="w-4 h-4 border-2 border-t-transparent rounded-full animate-spin" style={{
                          borderColor: '#dc2626'
                        }} />
                      ) : (
                        <UserMinus className="h-4 w-4" />
                      )}
                    </Button>
                  )}
                </div>
              )) || []}
            </div>
          </div>

          {/* Invite by Email */}
          <div className="p-4 rounded-xl border" style={{
            backgroundColor: '#dbeafe',
            borderColor: '#93c5fd'
          }}>
            <Label htmlFor="email" className="text-sm font-semibold flex items-center gap-2 mb-3" style={{ color: '#0f172a' }}>
              <Mail className="h-4 w-4" style={{ color: '#3b82f6' }} />
              Invite Family Member
            </Label>
            <div className="flex gap-2">
              <Input
                id="email"
                type="email"
                placeholder="Enter email address..."
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleInviteByEmail();
                  }
                }}
                className="transition-all duration-200"
                style={{
                  backgroundColor: '#ffffff',
                  borderColor: '#e2e8f0',
                  color: '#0f172a'
                }}
                onFocus={(e) => {
                  e.target.style.borderColor = '#3b82f6';
                  e.target.style.boxShadow = '0 0 0 3px rgba(59, 130, 246, 0.1)';
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = '#e2e8f0';
                  e.target.style.boxShadow = 'none';
                }}
              />
              <Button 
                onClick={handleInviteByEmail} 
                disabled={isInviting || !email.trim()}
                size="sm"
                className="transition-all duration-200 shadow-sm border-0"
                style={{
                  backgroundColor: '#3b82f6',
                  color: '#ffffff'
                }}
                onMouseEnter={(e) => {
                  if (!isInviting && email.trim()) {
                    e.currentTarget.style.backgroundColor = '#2563eb';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isInviting && email.trim()) {
                    e.currentTarget.style.backgroundColor = '#3b82f6';
                  }
                }}
              >
                {isInviting ? (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <>
                    <Mail className="h-4 w-4 mr-1" />
                    Invite
                  </>
                )}
              </Button>
            </div>
            <p className="text-xs mt-2 p-2 rounded border-l-2" style={{
              color: '#1e3a8a',
              backgroundColor: 'rgba(147, 197, 253, 0.5)',
              borderLeftColor: '#3b82f6'
            }}>
              📧 The person must already have a FamilyCart account to be invited.
            </p>
          </div>

          {/* Share Link */}
          <div className="p-4 rounded-xl border" style={{
            backgroundColor: '#f0fdf4',
            borderColor: '#bbf7d0'
          }}>
            <Label className="text-sm font-semibold flex items-center gap-2 mb-3" style={{ color: '#0f172a' }}>
              <Share className="h-4 w-4" style={{ color: '#22c55e' }} />
              Quick Share Link
            </Label>
            <div className="flex gap-2">
              <Input
                value={shareUrl}
                readOnly
                className="text-sm"
                style={{
                  backgroundColor: '#ffffff',
                  borderColor: '#e2e8f0',
                  color: '#64748b'
                }}
              />
              <Button 
                onClick={handleCopyShareUrl}
                variant="outline"
                size="sm"
                className="transition-colors"
                style={{
                  backgroundColor: '#ffffff',
                  borderColor: '#e2e8f0',
                  color: '#374151'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#f8fafc';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = '#ffffff';
                }}
              >
                {shareUrlCopied ? (
                  <Check className="h-4 w-4" style={{ color: '#22c55e' }} />
                ) : (
                  <Copy className="h-4 w-4" />
                )}
              </Button>
            </div>
            <p className="text-xs mt-2 flex items-center gap-1" style={{ color: '#166534' }}>
              <span className="w-1 h-1 rounded-full" style={{ backgroundColor: '#64748b' }}></span>
              Anyone with this link can view the list
            </p>
          </div>
        </div>

        <DialogFooter className="pt-2 sm:pt-4" style={{ borderTopColor: '#f1f5f9' }}>
          <Button 
            variant="outline" 
            onClick={onClose}
            className="w-full sm:w-auto transition-colors px-6"
            style={{
              backgroundColor: '#ffffff',
              borderColor: '#e2e8f0',
              color: '#374151'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#f8fafc';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = '#ffffff';
            }}
          >
            Done
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
