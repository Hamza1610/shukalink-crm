"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import {
    Sprout,
    LayoutDashboard,
    Package,
    Receipt,
    Users,
    Truck,
    MessageSquare,
    LogOut,
    Menu,
    X,
    PanelLeftClose,
} from "lucide-react";
import { useState } from "react";

const navigation = [
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { name: "Chat", href: "/chat", icon: MessageSquare },
    { name: "Produce", href: "/dashboard/produce", icon: Package },
    { name: "Transactions", href: "/dashboard/transactions", icon: Receipt },
    { name: "Relationships", href: "/dashboard/relationships", icon: Users },
    { name: "Logistics", href: "/dashboard/logistics", icon: Truck },
];

export function Sidebar({ isCollapsed, onToggleCollapse }: { isCollapsed?: boolean; onToggleCollapse?: () => void }) {
    const pathname = usePathname();
    const { user, logout } = useAuth();
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    const SidebarContent = () => (
        <>
            {/* Logo */}
            <div className="flex items-center gap-3 border-b border-gray-200 px-6 py-5">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-green-600 to-green-700">
                    <Sprout className="h-6 w-6 text-white" />
                </div>
                <div>
                    <h1 className="text-lg font-bold text-gray-900">ShukaLink</h1>
                    <p className="text-xs text-gray-500">CRM</p>
                </div>
            </div>

            {/* User Info */}
            <div className="border-b border-gray-200 px-6 py-4">
                <p className="text-sm font-medium text-gray-900">{user?.phone_number}</p>
                <p className="text-xs text-gray-500 capitalize">
                    {user?.user_type || "User"}
                </p>
            </div>

            {/* Navigation */}
            <nav className="flex-1 space-y-1 px-3 py-4">
                {navigation.map((item) => {
                    const isActive = pathname === item.href;
                    const Icon = item.icon;
                    return (
                        <Link
                            key={item.name}
                            href={item.href}
                            onClick={() => setMobileMenuOpen(false)}
                            className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${isActive
                                ? "bg-green-50 text-green-700"
                                : "text-gray-700 hover:bg-gray-100"
                                }`}
                        >
                            <Icon className="h-5 w-5" />
                            {item.name}
                        </Link>
                    );
                })}
            </nav>

            {/* Logout */}
            <div className="border-t border-gray-200 p-3 space-y-2">
                <button
                    onClick={logout}
                    className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-red-600 transition-colors hover:bg-red-50"
                >
                    <LogOut className="h-5 w-5" />
                    Logout
                </button>

                {/* Collapse Sidebar Toggle - Desktop only */}
                {onToggleCollapse && (
                    <button
                        onClick={onToggleCollapse}
                        className="hidden lg:flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-100"
                        title={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
                    >
                        <PanelLeftClose className="h-5 w-5" />
                        {isCollapsed ? "Expand" : "Collapse"}
                    </button>
                )}
            </div>
        </>
    );

    return (
        <>
            {/* Desktop Sidebar */}
            <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
                <div className="flex flex-col border-r border-gray-200 bg-white">
                    <SidebarContent />
                </div>
            </div>

            {/* Mobile Menu Button */}
            <div className="fixed top-0 left-0 right-0 z-40 flex items-center justify-between border-b border-gray-200 bg-white px-4 py-3 lg:hidden">
                <div className="flex items-center gap-2">
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-green-600 to-green-700">
                        <Sprout className="h-5 w-5 text-white" />
                    </div>
                    <span className="text-lg font-bold text-gray-900">ShukaLink</span>
                </div>
                <button
                    onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                    className="rounded-lg p-2 text-gray-600 hover:bg-gray-100"
                >
                    {mobileMenuOpen ? (
                        <X className="h-6 w-6" />
                    ) : (
                        <Menu className="h-6 w-6" />
                    )}
                </button>
            </div>

            {/* Mobile Sidebar */}
            {mobileMenuOpen && (
                <div className="fixed inset-0 z-30 lg:hidden">
                    <div
                        className="absolute inset-0 bg-gray-900/50"
                        onClick={() => setMobileMenuOpen(false)}
                    />
                    <div className="absolute inset-y-0 left-0 w-64 bg-white">
                        <div className="flex h-full flex-col pt-16">
                            <SidebarContent />
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}
