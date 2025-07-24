"use client";

import Image from 'next/image';
import Link from 'next/link';
import { cn } from '@/lib/utils';

interface LogoProps {
  variant?: 'cart-family' | 'connected-containers' | 'list' | 'logo' | 'tech-cart';
  size?: 'sm' | 'md' | 'lg' | 'xl' | '2xl';
  showText?: boolean;
  className?: string;
  href?: string;
}

const sizeConfig = {
  sm: {
    image: 'h-6 w-6',
    text: 'text-lg font-headline font-bold',
    gap: 'gap-1.5'
  },
  md: {
    image: 'h-8 w-8 sm:h-9 sm:w-9',
    text: 'text-xl sm:text-2xl font-headline font-bold',
    gap: 'gap-2'
  },
  lg: {
    image: 'h-8 w-8 sm:h-10 sm:w-10',
    text: 'text-xl sm:text-2xl font-headline font-bold',
    gap: 'gap-2'
  },
  xl: {
    image: 'h-10 w-10 sm:h-12 sm:w-12',
    text: 'text-2xl sm:text-3xl font-headline font-bold',
    gap: 'gap-2 sm:gap-3'
  },
  '2xl': {
    image: 'h-10 w-10 sm:h-14 sm:w-14',
    text: 'text-2xl sm:text-4xl font-headline font-bold',
    gap: 'gap-2 sm:gap-4'
  }
};

export function FamilyCartLogo({ 
  variant = 'cart-family', 
  size = 'lg', 
  showText = true, 
  className = '',
  href
}: LogoProps) {
  const config = sizeConfig[size];
  
  // Smart variant selection: use simplified logo for small sizes
  const getOptimalVariant = (requestedVariant: string, size: string) => {
    if (size === 'sm' && requestedVariant === 'cart-family') {
      // For small sizes, use a simpler variant that's more readable
      return 'list'; // or 'logo' - whichever is simpler
    }
    return requestedVariant;
  };
  
  const optimalVariant = getOptimalVariant(variant, size);
  
  const logoContent = (
    <div className={cn('flex items-center', config.gap, className)}>
      <Image
        src={`/logo/${optimalVariant}.png`}
        alt="FamilyCart Logo"
        width={48}
        height={48}
        className={cn(config.image, 'object-contain')}

        priority
      />
      {showText && (
        <span className={cn(config.text, 'text-primary')}>
          FamilyCart
        </span>
      )}
    </div>
  );

  if (href) {
    return (
      <Link href={href} className="flex items-center">
        {logoContent}
      </Link>
    );
  }

  return logoContent;
}

// Individual logo variants for specific use cases
export function LogoIconOnly({ 
  variant = 'cart-family', 
  size = 'md', 
  className = '' 
}: Pick<LogoProps, 'variant' | 'size' | 'className'>) {
  return (
    <FamilyCartLogo 
      variant={variant} 
      size={size} 
      showText={false} 
      className={className} 
    />
  );
}

export function LogoWithText({ 
  variant = 'cart-family', 
  size = 'lg', 
  className = '',
  href = '/dashboard'
}: LogoProps) {
  return (
    <FamilyCartLogo 
      variant={variant} 
      size={size} 
      showText={true} 
      className={className}
      href={href}
    />
  );
}
