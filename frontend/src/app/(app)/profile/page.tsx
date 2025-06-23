"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import type { ShoppingList } from '@/types';
import axios from 'axios';

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { useToast } from "@/hooks/use-toast";
import { Loader2, Save, UserCircle, Mail, LogOut, Trash2 } from 'lucide-react';

export default function ProfilePage() {
  const { user, token, loading, logout, fetchUser } = useAuth();
  const [ownedLists, setOwnedLists] = useState<ShoppingList[]>([]);
  const [sharedLists, setSharedLists] = useState<ShoppingList[]>([]);
  
  const [newFullName, setNewFullName] = useState('');
  const [newEmail, setNewEmail] = useState('');

  const [isUpdating, setIsUpdating] = useState(false);

  const router = useRouter();
  const { toast } = useToast();

  useEffect(() => {
    if (!loading && !user) {
      router.push('/login');
    }
    if (user) {
      setNewFullName(user.full_name || '');
      setNewEmail(user.email || '');
      fetchUserLists();
    }
  }, [user, loading, router]);

  const fetchUserLists = async () => {
    if (!token || !user) return;
    try {
      const { data } = await axios.get<ShoppingList[]>('/api/v1/shopping-lists', {
        headers: { Authorization: `Bearer ${token}` },
      });
      const owned = data.filter(list => list.owner_id === user.id);
      const shared = data.filter(list => list.owner_id !== user.id);
      setOwnedLists(owned);
      setSharedLists(shared);
    } catch (error) {
      console.error("Error fetching user lists:", error);
      toast({ title: "Error", description: "Could not fetch your shopping lists.", variant: "destructive" });
    }
  };

  const handleProfileUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user || !token) return;
    setIsUpdating(true);

    const updatedData: { email?: string; full_name?: string } = {};
    if (newEmail !== user.email) updatedData.email = newEmail;
    if (newFullName !== user.full_name) updatedData.full_name = newFullName;

    if (Object.keys(updatedData).length === 0) {
      toast({ title: "No changes to save." });
      setIsUpdating(false);
      return;
    }

    try {
      await axios.put('/api/v1/users/me', updatedData, {
        headers: { Authorization: `Bearer ${token}` },
      });
      toast({ title: "Profile Updated", description: "Your profile has been successfully updated." });
      if (fetchUser) {
        await fetchUser();
      }
    } catch (error) {
      console.error("Error updating profile:", error);
      toast({ title: "Update Failed", description: "Could not update your profile.", variant: "destructive" });
    } finally {
      setIsUpdating(false);
    }
  };

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  const handleDeleteAccount = async () => {
    if (!window.confirm("Are you sure you want to delete your account? This action is irreversible.")) return;
    
    try {
      await axios.delete('/api/v1/users/me', {
        headers: { Authorization: `Bearer ${token}` },
      });
      toast({ title: "Account Deleted", description: "Your account has been permanently deleted." });
      logout();
    } catch (error) {
      console.error("Error deleting account:", error);
      toast({ title: "Deletion Failed", description: "Could not delete your account.", variant: "destructive" });
    }
  };

  if (loading || !user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-12 w-12 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4 md:p-8">
      <header className="mb-8">
        <h1 className="text-4xl font-bold font-headline">Your Profile</h1>
        <p className="text-muted-foreground">Manage your account details and view your lists.</p>
      </header>

      <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
        {/* Profile Details Card */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle>Account Details</CardTitle>
            <CardDescription>Update your name and email address.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleProfileUpdate} className="space-y-6">
              <div className="flex items-center space-x-4">
                <Avatar className="h-16 w-16">
                  <AvatarImage src={`https://api.dicebear.com/8.x/initials/svg?seed=${user.full_name || user.email}`}/>
                  <AvatarFallback>{(user.full_name || user.email || 'U').charAt(0).toUpperCase()}</AvatarFallback>
                </Avatar>
                <div>
                  <h2 className="text-xl font-semibold">{user.full_name || 'New User'}</h2>
                  <p className="text-sm text-muted-foreground">{user.email}</p>
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="fullName"><UserCircle className="inline-block mr-2 h-4 w-4"/>Full Name</Label>
                <Input 
                  id="fullName" 
                  value={newFullName} 
                  onChange={(e) => setNewFullName(e.target.value)} 
                  placeholder="Your full name"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email"><Mail className="inline-block mr-2 h-4 w-4"/>Email Address</Label>
                <Input 
                  id="email" 
                  type="email" 
                  value={newEmail} 
                  onChange={(e) => setNewEmail(e.target.value)} 
                  placeholder="your@email.com"
                />
              </div>
              <Button type="submit" disabled={isUpdating} className="w-full">
                {isUpdating ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />} 
                Save Changes
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Lists Overview Card */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>My Shopping Lists</CardTitle>
            <CardDescription>An overview of lists you own and are a member of.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h3 className="font-semibold mb-2">Owned by You ({ownedLists.length})</h3>
              {ownedLists.length > 0 ? (
                <ul className="space-y-2">
                  {ownedLists.map(list => <li key={list.id} className="p-2 rounded-md bg-muted/50 text-sm">{list.name}</li>)}
                </ul>
              ) : (
                <p className="text-sm text-muted-foreground italic">You haven't created any lists yet.</p>
              )}
            </div>
            <div>
              <h3 className="font-semibold mb-2">Shared with You ({sharedLists.length})</h3>
              {sharedLists.length > 0 ? (
                <ul className="space-y-2">
                  {sharedLists.map(list => <li key={list.id} className="p-2 rounded-md bg-muted/50 text-sm">{list.name}</li>)}
                </ul>
              ) : (
                <p className="text-sm text-muted-foreground italic">No lists have been shared with you.</p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Account Actions Card */}
        <Card className="lg:col-span-3">
          <CardHeader>
            <CardTitle>Account Actions</CardTitle>
            <CardDescription>Manage your account session and data.</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col sm:flex-row gap-4">
            <Button variant="outline" onClick={handleLogout} className="w-full sm:w-auto">
              <LogOut className="mr-2 h-4 w-4" /> Sign Out
            </Button>
            <Button variant="destructive" onClick={handleDeleteAccount} className="w-full sm:w-auto">
              <Trash2 className="mr-2 h-4 w-4" /> Delete Account
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
