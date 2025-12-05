/**
 * Old Chat Page - Redirects to standalone chat
 */
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function OldChatPage() {
    const router = useRouter();

    useEffect(() => {
        // Redirect to new standalone chat page
        router.replace('/chat');
    }, [router]);

    return (
        <div className="flex items-center justify-center h-screen">
            <div className="text-center">
                <div className="w-16 h-16 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                <p className="text-slate-600 dark:text-slate-400">Redirecting to chat...</p>
            </div>
        </div>
    );
}
