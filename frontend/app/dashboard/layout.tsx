"use client";

import { useState } from "react";
import ProtectedRoute from "@/components/protected-route";
import { Sidebar } from "@/components/sidebar";

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
    
    return (
        <ProtectedRoute>
            <div className="flex h-screen overflow-hidden bg-gray-50">
                {/* Sidebar - hide completely when collapsed */}
                <div 
                    className={`transition-all duration-300 ${isSidebarCollapsed ? 'hidden lg:hidden' : ''}`}
                >
                    <Sidebar 
                        isCollapsed={isSidebarCollapsed} 
                        onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)} 
                    />
                </div>
                
                {/* Main content - adjust padding based on sidebar state */}
                <main className={`flex-1 overflow-y-auto transition-all duration-300 ${isSidebarCollapsed ? '' : 'lg:pl-64'}`}>
                    <div className="pt-16 lg:pt-0">
                        {children}
                    </div>
                </main>
            </div>
        </ProtectedRoute>
    );
}
