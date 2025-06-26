/**
 * Utility functions for generating consistent user colors and avatars
 */

/**
 * Generates a consistent color for a user based on their identifier
 * Uses a hash function to ensure the same user always gets the same color
 * @param userId - User ID (string)
 * @param userEmail - User email as fallback
 * @param userNickname - User nickname as fallback
 * @returns Object with color classes and hex values
 */
export function getUserColor(userId: string, userEmail?: string, userNickname?: string) {
  // Use userId first, then email, then nickname as seed
  const seed = userId || userEmail || userNickname || 'unknown';
  
  // Simple hash function to generate consistent colors
  let hash = 0;
  for (let i = 0; i < seed.length; i++) {
    const char = seed.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  
  // Predefined color palette that works well with our design system
  const colorPalette = [
    {
      name: 'blue',
      bg: 'bg-blue-100',
      border: 'border-blue-200',
      text: 'text-blue-700',
      accent: 'bg-blue-500',
      hex: '#3B82F6'
    },
    {
      name: 'green',
      bg: 'bg-green-100',
      border: 'border-green-200', 
      text: 'text-green-700',
      accent: 'bg-green-500',
      hex: '#10B981'
    },
    {
      name: 'purple',
      bg: 'bg-purple-100',
      border: 'border-purple-200',
      text: 'text-purple-700',
      accent: 'bg-purple-500',
      hex: '#8B5CF6'
    },
    {
      name: 'orange',
      bg: 'bg-orange-100',
      border: 'border-orange-200',
      text: 'text-orange-700',
      accent: 'bg-orange-500',
      hex: '#F97316'
    },
    {
      name: 'pink',
      bg: 'bg-pink-100',
      border: 'border-pink-200',
      text: 'text-pink-700',
      accent: 'bg-pink-500',
      hex: '#EC4899'
    },
    {
      name: 'indigo',
      bg: 'bg-indigo-100',
      border: 'border-indigo-200',
      text: 'text-indigo-700',
      accent: 'bg-indigo-500',
      hex: '#6366F1'
    },
    {
      name: 'teal',
      bg: 'bg-teal-100',
      border: 'border-teal-200',
      text: 'text-teal-700',
      accent: 'bg-teal-500',
      hex: '#14B8A6'
    },
    {
      name: 'red',
      bg: 'bg-red-100',
      border: 'border-red-200',
      text: 'text-red-700',
      accent: 'bg-red-500',
      hex: '#EF4444'
    },
    {
      name: 'emerald',
      bg: 'bg-emerald-100',
      border: 'border-emerald-200',
      text: 'text-emerald-700',
      accent: 'bg-emerald-500',
      hex: '#059669'
    },
    {
      name: 'violet',
      bg: 'bg-violet-100',
      border: 'border-violet-200',
      text: 'text-violet-700',
      accent: 'bg-violet-500',
      hex: '#7C3AED'
    }
  ];
  
  // Use hash to select color consistently
  const colorIndex = Math.abs(hash) % colorPalette.length;
  return colorPalette[colorIndex];
}

/**
 * Gets user initials for display
 * @param fullName - User's full name
 * @param email - User's email as fallback
 * @param nickname - User's nickname as fallback
 * @returns User initials (max 2 characters)
 */
export function getUserInitials(fullName?: string | null, email?: string | null, nickname?: string | null): string {
  if (fullName) {
    return fullName.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  }
  if (nickname) {
    return nickname.slice(0, 2).toUpperCase();
  }
  if (email) {
    return email.substring(0, 2).toUpperCase();
  }
  return "FC"; // FamilyCart fallback
}

/**
 * Generates a DiceBear avatar URL for consistent avatar generation
 * @param seed - Seed for avatar generation (userId, email, or nickname)
 * @param style - DiceBear style (default: 'initials')
 * @param size - Avatar size (default: 40)
 * @returns DiceBear avatar URL
 */
export function getDiceBearAvatarUrl(seed: string, style: string = 'initials', size: number = 40): string {
  return `https://api.dicebear.com/8.x/${style}/svg?seed=${encodeURIComponent(seed)}&size=${size}`;
}

/**
 * Creates a user badge component data for consistent user representation
 * @param user - User object with id, email, nickname, full_name
 * @returns Object with all necessary data for user badge display
 */
export function createUserBadge(user: {
  id: string;
  email?: string;
  nickname?: string;
  full_name?: string;
}) {
  const color = getUserColor(user.id, user.email, user.nickname);
  const initials = getUserInitials(user.full_name, user.email, user.nickname);
  const displayName = user.nickname || user.full_name || user.email || 'Unknown User';
  const avatarUrl = getDiceBearAvatarUrl(user.full_name || user.email || user.id);
  
  return {
    user,
    color,
    initials,
    displayName,
    avatarUrl
  };
}
