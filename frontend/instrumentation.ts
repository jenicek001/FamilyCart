/**
 * Next.js Instrumentation File
 * 
 * This file is required for Next.js 15.4+ to resolve the private-next-instrumentation-client module.
 * It can be used to register OpenTelemetry, custom monitoring, or other server/client initialization hooks.
 * 
 * @see https://nextjs.org/docs/app/api-reference/file-conventions/instrumentation
 */

/**
 * Called when the server starts (both Node.js and Edge runtimes)
 * Use this for initializing monitoring, tracing, or other server-side setup
 */
export async function register() {
  // Server-side initialization logic goes here
  // Example: registerOTel({ serviceName: 'familycart' })
}
