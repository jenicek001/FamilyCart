"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { onAuthStateChanged, updateProfile as updateAuthProfile, updateEmail, reauthenticateWithCredential, EmailAuthProvider } from 'firebase/auth';
import { auth, db } from '@/lib/firebase/firebase';
import { doc, getDoc, updateDoc, collection, query, where, getDocs, arrayRemove, writeBatch } from 'firebase/firestore';
import type { User } from 'firebase/auth';
import type { ShoppingList, UserProfile as UserProfileType } from '@/types';

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { useToast } from "@/hooks/use-toast";
import { Loader2, Edit3, Save, UserCircle, Mail, ShieldCheck, LogOut, Trash2, ListChecks } from 'lucide-react';
import type { Metadata } from 'next';

// export const metadata: Metadata = {
//   title: 'Profile - FamilyCart',
//   description: 'Manage your FamilyCart profile and shopping lists.',
// };

export default function ProfilePage() {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [userProfile, setUserProfile] = useState<UserProfileType | null>(null);
  const [ownedLists, setOwnedLists] = useState<ShoppingList[]>([]);
  const [sharedLists, setSharedLists] = useState<ShoppingList[]>([]);
  
  const [newNickname, setNewNickname] = useState('');
  const [newEmail, setNewEmail] = useState('');
  const [currentPassword, setCurrentPassword] = useState(''); // For re-authentication

  const [isLoading, setIsLoading] = useState(true);
  const [isUpdating, setIsUpdating] = useState(false);

  const router = useRouter();
  const { toast } = useToast();

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      if (user) {
        setCurrentUser(user);
        await fetchUserProfile(user.uid);
        await fetchUserLists(user.uid);
      } else {
        router.push('/login');
      }
      setIsLoading(false);
    });
    return () => unsubscribe();
  }, [router]);

  const fetchUserProfile = async (uid: string) => {
    const userDocRef = doc(db, "users", uid);
    const userDocSnap = await getDoc(userDocRef);
    if (userDocSnap.exists()) {
      const profileData = userDocSnap.data() as UserProfileType;
      setUserProfile(profileData);
      setNewNickname(profileData.nickname || '');
      setNewEmail(profileData.email || '');
    } else {
      // Fallback if no profile in Firestore, use auth data
      const authUser = auth.currentUser;
      if (authUser) {
        const fallbackProfile = { 
          uid: authUser.uid, 
          email: authUser.email, 
          nickname: authUser.displayName || authUser.email?.split('@')[0] || 'User'
        };
        setUserProfile(fallbackProfile);
        setNewNickname(fallbackProfile.nickname);
        setNewEmail(fallbackProfile.email || '');
      }
    }
  };

  const fetchUserLists = async (uid: string) => {
    // Owned lists
    const ownedQuery = query(collection(db, "shoppingLists"), where("ownerUid", "==", uid));
    const ownedSnapshot = await getDocs(ownedQuery);
    const fetchedOwnedLists = ownedSnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() } as ShoppingList));
    setOwnedLists(fetchedOwnedLists);

    // Shared lists (where user is a member but not owner)
    const sharedQuery = query(collection(db, "shoppingLists"), where("members", "array-contains", uid));
    const sharedSnapshot = await getDocs(sharedQuery);
    const fetchedSharedLists = sharedSnapshot.docs
      .map(doc => ({ id: doc.id, ...doc.data() } as ShoppingList))
      .filter(list => list.ownerUid !== uid);
    setSharedLists(fetchedSharedLists);
  };

  const handleProfileUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentUser || !userProfile) return;
    setIsUpdating(true);

    try {
      // Re-authenticate if email is changing
      if (newEmail !== currentUser.email && currentPassword) {
        const credential = EmailAuthProvider.credential(currentUser.email!, currentPassword);
        await reauthenticateWithCredential(currentUser, credential);
        await updateEmail(currentUser, newEmail);
      } else if (newEmail !== currentUser.email && !currentPassword) {
         toast({ title: "Password Required", description: "Please enter your current password to change your email.", variant: "destructive" });
         setIsUpdating(false);
         return;
      }
      
      // Update Firebase Auth display name
      if (newNickname !== currentUser.displayName) {
        await updateAuthProfile(currentUser, { displayName: newNickname });
      }

      // Update Firestore profile
      const userDocRef = doc(db, "users", currentUser.uid);
      await updateDoc(userDocRef, {
        nickname: newNickname,
        email: newEmail, // Keep Firestore email in sync
      });

      setUserProfile(prev => prev ? {...prev, nickname: newNickname, email: newEmail} : null);
      toast({ title: "Profile Updated", description: "Your profile has been successfully updated." });
      setCurrentPassword(''); // Clear password field
    } catch (error: any) {
      console.error("Error updating profile:", error);
      toast({ title: "Update Failed", description: error.message || "Could not update profile.", variant: "destructive" });
    } finally {
      setIsUpdating(false);
    }
  };
  
  const handleLeaveList = async (listId: string) => {
    if (!currentUser) return;
    if (!confirm("Are you sure you want to leave this list?")) return;

    try {
      const listRef = doc(db, "shoppingLists", listId);
      await updateDoc(listRef, {
        members: arrayRemove(currentUser.uid)
      });
      setSharedLists(prev => prev.filter(list => list.id !== listId));
      toast({ title: "Left List", description: "You have successfully left the shopping list." });
    } catch (error: any) {
      console.error("Error leaving list:", error);
      toast({ title: "Error", description: "Could not leave the list.", variant: "destructive" });
    }
  };
  
  const handleDeleteOwnedList = async (listId: string) => {
     if (!confirm("Are you sure you want to PERMANENTLY DELETE this list? This action cannot be undone.")) return;
    try {
      await deleteDoc(doc(db, "shoppingLists", listId));
      setOwnedLists(prevLists => prevLists.filter(list => list.id !== listId));
      toast({ title: "List Deleted", description: "The shopping list has been permanently deleted." });
    } catch (error) {
      console.error("Error deleting list: ", error);
      toast({ title: "Error", description: "Could not delete list.", variant: "destructive" });
    }
  };


  if (isLoading || !userProfile || !currentUser) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-theme(spacing.32))]">
        <Loader2 className="h-12 w-12 animate-spin text-primary" />
        <p className="ml-4 text-lg">Loading your profile...</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <header className="mb-8">
        <h2 className="text-3xl font-headline font-bold flex items-center">
          <UserCircle className="mr-3 h-8 w-8 text-primary" /> Your Profile
        </h2>
        <p className="text-muted-foreground">Manage your account details and shopping lists.</p>
      </header>

      <Card>
        <CardHeader>
          <CardTitle className="font-headline text-xl flex items-center"><Edit3 className="mr-2 h-5 w-5" /> Edit Profile</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleProfileUpdate} className="space-y-6">
            <div className="flex items-center gap-4 mb-6">
                <Avatar className="h-20 w-20">
                    <AvatarImage src={currentUser.photoURL || undefined} alt={userProfile.nickname} data-ai-hint="avatar user"/>
                    <AvatarFallback className="text-2xl">
                        {userProfile.nickname?.substring(0,2).toUpperCase() || currentUser.email?.substring(0,2).toUpperCase()}
                    </AvatarFallback>
                </Avatar>
                {/* Placeholder for image upload - complex feature
                <Button type="button" variant="outline">Change Picture</Button>
                */}
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="nickname">Nickname</Label>
                <div className="relative">
                    <UserCircle className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                    <Input id="nickname" value={newNickname} onChange={(e) => setNewNickname(e.target.value)} className="pl-10" />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email Address</Label>
                 <div className="relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                    <Input id="email" type="email" value={newEmail} onChange={(e) => setNewEmail(e.target.value)} className="pl-10" />
                </div>
              </div>
            </div>
            {newEmail !== currentUser.email && (
                 <div className="space-y-2 pt-2 border-t border-border">
                    <Label htmlFor="currentPassword">Current Password (to change email)</Label>
                    <div className="relative">
                        <ShieldCheck className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                        <Input id="currentPassword" type="password" value={currentPassword} onChange={(e) => setCurrentPassword(e.target.value)} placeholder="Enter current password" className="pl-10" />
                    </div>
                    <p className="text-xs text-muted-foreground">Required if you are changing your email address.</p>
                </div>
            )}
            <Button type="submit" disabled={isUpdating} className="bg-primary hover:bg-primary/90 text-primary-foreground">
              {isUpdating ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
              Save Changes
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="font-headline text-xl flex items-center"><ListChecks className="mr-2 h-5 w-5 text-primary" /> My Shopping Lists (Owned)</CardTitle>
          <CardDescription>Lists you have created and can manage fully.</CardDescription>
        </CardHeader>
        <CardContent>
          {ownedLists.length === 0 ? (
            <p className="text-muted-foreground">You haven&apos;t created any lists yet.</p>
          ) : (
            <ul className="space-y-3">
              {ownedLists.map(list => (
                <li key={list.id} className="flex justify-between items-center p-3 border rounded-md hover:bg-muted/50">
                  <span>{list.name}</span>
                  <Button variant="destructive" size="sm" onClick={() => handleDeleteOwnedList(list.id)}>
                    <Trash2 className="mr-2 h-4 w-4" /> Delete
                  </Button>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader>
          <CardTitle className="font-headline text-xl flex items-center"><ListChecks className="mr-2 h-5 w-5 text-accent" /> Lists Shared With Me</CardTitle>
           <CardDescription>Lists created by others that you are a member of.</CardDescription>
        </CardHeader>
        <CardContent>
          {sharedLists.length === 0 ? (
            <p className="text-muted-foreground">No lists have been shared with you yet.</p>
          ) : (
            <ul className="space-y-3">
              {sharedLists.map(list => (
                <li key={list.id} className="flex justify-between items-center p-3 border rounded-md hover:bg-muted/50">
                  <div>
                    <span className="font-medium">{list.name}</span>
                    {/* In a real app, you'd fetch owner's nickname */}
                    <p className="text-xs text-muted-foreground">Owned by: {list.ownerUid.substring(0,8)}...</p>
                  </div>
                  <Button variant="outline" size="sm" onClick={() => handleLeaveList(list.id)}>
                    <LogOut className="mr-2 h-4 w-4" /> Leave List
                  </Button>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

    </div>
  );
}
