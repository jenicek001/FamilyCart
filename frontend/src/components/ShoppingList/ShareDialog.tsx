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
      <DialogContent className="max-w-md bg-white border border-gray-200 shadow-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-gray-900">
            <Share className="h-5 w-5" />
            Share "{list.name}"
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Current Members */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="text-sm font-medium mb-3 text-gray-900">Members ({(list.members?.length || 0) + 1})</h4>
            <div className="space-y-2">
              {/* Owner */}
              <div className="flex items-center justify-between p-3 bg-white border border-gray-200 rounded-lg shadow-sm">
                <div className="flex items-center gap-3">
                  {isOwner && user ? (
                    <UserBadge user={user} size="sm" showName />
                  ) : (
                    <div className="flex items-center gap-2">
                      <div className="w-6 h-6 bg-gray-300 rounded-full flex items-center justify-center">
                        <span className="text-xs text-gray-700">?</span>
                      </div>
                      <span className="text-sm text-gray-900">Owner</span>
                    </div>
                  )}
                  <Crown className="h-4 w-4 text-yellow-500" />
                </div>
                <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">Owner</span>
              </div>
              
              {/* Members */}
              {list.members?.map((member) => (
                <div key={member.id} className="flex items-center justify-between p-3 bg-white border border-gray-200 rounded-lg shadow-sm">
                  <UserBadge user={member} size="sm" showName />
                  {isOwner && member.id !== user?.id && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleRemoveMember(member.id)}
                      disabled={isRemoving === member.id}
                      className="text-red-600 hover:text-red-700 hover:bg-red-50 bg-white border border-red-200"
                    >
                      <UserMinus className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              )) || []}
            </div>
          </div>

          {/* Invite by Email */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <Label htmlFor="email" className="text-sm font-medium text-gray-900">
              Invite by email
            </Label>
            <div className="flex gap-2 mt-2">
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
                className="bg-white border-gray-300 text-gray-900 placeholder-gray-500"
              />
              <Button 
                onClick={handleInviteByEmail} 
                disabled={isInviting || !email.trim()}
                size="sm"
                className="bg-blue-600 hover:bg-blue-700 text-white border-0 shadow-sm"
              >
                <Mail className="h-4 w-4 mr-1" />
                {isInviting ? 'Sending...' : 'Invite'}
              </Button>
            </div>
            <p className="text-xs text-gray-600 mt-2 bg-blue-50 p-2 rounded border-l-2 border-blue-300">
              Note: The person must already have a FamilyCart account to be invited.
            </p>
          </div>

          {/* Share Link */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <Label className="text-sm font-medium text-gray-900">Share link</Label>
            <div className="flex gap-2 mt-2">
              <Input
                value={shareUrl}
                readOnly
                className="text-sm bg-white border-gray-300 text-gray-900"
              />
              <Button 
                onClick={handleCopyShareUrl}
                variant="outline"
                size="sm"
                className="bg-white border-gray-300 hover:bg-gray-50 text-gray-700"
              >
                {shareUrlCopied ? (
                  <Check className="h-4 w-4 text-green-600" />
                ) : (
                  <Copy className="h-4 w-4" />
                )}
              </Button>
            </div>
            <p className="text-xs text-gray-600 mt-2">
              Anyone with this link can view the list
            </p>
          </div>
        </div>

        <DialogFooter className="pt-4 border-t border-gray-200">
          <Button 
            variant="outline" 
            onClick={onClose}
            className="bg-white border-gray-300 hover:bg-gray-50 text-gray-700 shadow-sm"
          >
            Done
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
