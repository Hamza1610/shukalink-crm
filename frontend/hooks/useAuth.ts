"use client";

import { useEffect, useState } from "react";
import { authApi, type User } from "@/lib/api";

interface AuthContextType {
    user: User | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    logout: () => void;
}

export function useAuth(): AuthContextType {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        // Check if user is already authenticated
        const currentUser = authApi.getCurrentUser();
        setUser(currentUser);
        setIsLoading(false);
    }, []);

    const logout = () => {
        authApi.logout();
        setUser(null);
        window.location.href = "/auth/login";
    };

    return {
        user,
        isAuthenticated: !!user,
        isLoading,
        logout,
    };
}
