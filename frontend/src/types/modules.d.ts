// Type declarations for module resolution

declare module '@/lib/utils' {
  import { ClassValue } from 'clsx';
  export function cn(...inputs: ClassValue[]): string;
}

declare module '@/lib/*' {
  const content: any;
  export default content;
}

declare module '@/components/*' {
  const content: any;
  export default content;
}