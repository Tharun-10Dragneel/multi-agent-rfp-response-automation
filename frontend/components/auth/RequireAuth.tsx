"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { FullPageLoader } from "@/components/ui/spinner";

export default function RequireAuth({ children, redirectTo = "/login" }) {
  const router = useRouter();
  const { isAuthenticated, loading } = useAuth();

  useEffect(() => {
    if (loading) return;
    if (!isAuthenticated) {
      router.replace(redirectTo);
    }
  }, [isAuthenticated, loading, redirectTo, router]);

  if (loading) return <FullPageLoader text="Authenticating..." subtext="Please wait while we verify your session" />;
  if (!isAuthenticated) return <FullPageLoader text="Redirecting..." subtext="Taking you to the login page" />;

  return children;
}
