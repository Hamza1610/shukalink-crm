/**
 * Standalone Chat Page Layout
 * Full-screen experience without dashboard interference
 */
"use client";

import ProtectedRoute from "@/components/protected-route";

export default function ChatLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <ProtectedRoute>
            {/* Full screen - no dashboard layout */}
            <div className="h-screen w-screen overflow-hidden bg-slate-50 dark:bg-slate-900">
                {children}
            </div>
        </ProtectedRoute>
    );
}
