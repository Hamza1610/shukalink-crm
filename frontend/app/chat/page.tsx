/**
 * Standalone Chat Page
 * Full-screen AI chat experience
 */
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import ChatInterface from '@/components/ChatInterface';
import { useAuth } from '@/hooks/useAuth';
import { ArrowLeft, Minimize2 } from 'lucide-react';

export default function StandaloneChatPage() {
    const router = useRouter();
    const { user, isAuthenticated, isLoading } = useAuth();

    // Get token from localStorage - managed by useAuth
    const getToken = () => localStorage.getItem('auth_token');

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-screen bg-slate-50 dark:bg-slate-900">
                <div className="text-center">
                    <div className="w-16 h-16 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                    <p className="text-slate-600 dark:text-slate-400">Loading chat...</p>
                </div>
            </div>
        );
    }

    if (!isAuthenticated || !user) {
        router.push('/login');
        return null;
    }

    const token = getToken();
    if (!token) {
        router.push('/login');
        return null;
    }

    return (
        <div className="flex flex-col h-screen">
            {/* Minimal Header */}
            <div className="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 px-4 py-3 flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <button
                        onClick={() => router.push('/dashboard')}
                        className="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
                        title="Back to Dashboard"
                    >
                        <ArrowLeft className="w-5 h-5 text-slate-600 dark:text-slate-300" />
                    </button>
                    <div>
                        <h1 className="text-lg font-semibold text-slate-900 dark:text-white">
                            ShukaLink Chat
                        </h1>
                        <p className="text-xs text-slate-500 dark:text-slate-400">
                            AI Assistant
                        </p>
                    </div>
                </div>

                <button
                    onClick={() => router.push('/dashboard')}
                    className="hidden md:flex items-center gap-2 px-3 py-2 text-sm text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
                >
                    <Minimize2 className="w-4 h-4" />
                    Minimize
                </button>
            </div>

            {/* Full Screen Chat */}
            <div className="flex-1 overflow-hidden">
                <ChatInterface userId={user.id} token={token} />
            </div>
        </div>
    );
}
