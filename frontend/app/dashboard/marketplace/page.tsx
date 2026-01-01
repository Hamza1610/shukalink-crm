/**
 * Marketplace Page
 * Buyers can browse produce, filter, search, and contact farmers
 */
'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { Search, Filter, MapPin, X } from 'lucide-react';
import ProduceCard from '@/components/ProduceCard';
import { useRouter } from 'next/navigation';

interface Produce {
    id: string;
    crop_type: string;
    quantity_kg: number;
    price_per_kg: number;
    harvest_date: string;
    status: 'available' | 'reserved' | 'sold';
    quality_indicators?: string[];
    images?: string[];
    location?: string;
    farmer_id?: string;
}

export default function MarketplacePage() {
    const { user } = useAuth();
    const router = useRouter();
    const [produces, setProduces] = useState<Produce[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filters, setFilters] = useState({
        crop_type: '',
        max_price: '',
        min_quantity: ''
    });
    const [showFilters, setShowFilters] = useState(false);

    useEffect(() => {
        fetchMarketplace();
    }, [filters, searchTerm]); // Debounce could be added for search

    const fetchMarketplace = async () => {
        setIsLoading(true);
        try {
            const token = localStorage.getItem('auth_token');

            // Build query params
            const params = new URLSearchParams();
            if (filters.crop_type) params.append('crop_type', filters.crop_type);
            if (filters.max_price) params.append('max_price', filters.max_price);
            if (filters.min_quantity) params.append('min_quantity', filters.min_quantity);
            // Search term usually fits into crop_type or generic search if backend supports it.
            // For now, let's assume search maps to crop_type if manually typed, 
            // but ideally we'd have a 'q' param. We'll use client-side filter for fuzzy search 
            // or assume crop_type for now if search matches known crops. 
            // To keep it simple, we'll just use the explicit filters for API and maybe 
            // client-side search or map search to query params if reliable.

            // Let's rely on the separate Filter UI for strict filtering
            // and maybe mapped text search later.

            const response = await fetch(
                `http://localhost:8000/api/v1/produce/?${params.toString()}`,
                {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                }
            );

            if (response.ok) {
                const data = await response.json();
                // Client-side text filter if needed
                const filtered = searchTerm
                    ? data.filter((p: Produce) =>
                        p.crop_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
                        p.location?.toLowerCase().includes(searchTerm.toLowerCase()))
                    : data;
                setProduces(filtered);
            }
        } catch (error) {
            console.error('Error fetching marketplace:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleContactFarmer = (produce: Produce) => {
        // Navigate to chat with pre-filled message
        // We'll need a way to start chat with generic user.
        // Ideally: router.push(`/chat?recipient=${produce.farmer_id}&ref=produce_${produce.id}`)
        alert(`Starting chat with farmer for ${produce.crop_type}... (Feature coming soon)`);
        router.push('/chat');
    };

    return (
        <div className="flex bg-gray-50 dark:bg-gray-900 min-h-screen">

            {/* Sidebar Filters (Desktop) */}
            <div className={`
                fixed inset-y-0 left-0 lg:static w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transform transition-transform z-30
                ${showFilters ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
            `}>
                <div className="p-6 h-full overflow-y-auto">
                    <div className="flex justify-between items-center mb-6 lg:hidden">
                        <h2 className="font-bold text-lg">Filters</h2>
                        <button onClick={() => setShowFilters(false)}>
                            <X className="w-5 h-5" />
                        </button>
                    </div>

                    <h2 className="font-bold text-lg text-gray-900 dark:text-white mb-4 hidden lg:block">
                        Filters
                    </h2>

                    <div className="space-y-6">
                        {/* Crop Type Filter */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Crop Type
                            </label>
                            <select
                                value={filters.crop_type}
                                onChange={(e) => setFilters({ ...filters, crop_type: e.target.value })}
                                className="w-full bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg px-3 py-2 text-sm"
                            >
                                <option value="">All Crops</option>
                                <option value="Maize">Maize</option>
                                <option value="Rice">Rice</option>
                                <option value="Tomatoes">Tomatoes</option>
                                <option value="Beans">Beans</option>
                                <option value="Cassava">Cassava</option>
                                <option value="Yam">Yam</option>
                            </select>
                        </div>

                        {/* Price Range */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Max Price / kg (₦)
                            </label>
                            <input
                                type="number"
                                value={filters.max_price}
                                onChange={(e) => setFilters({ ...filters, max_price: e.target.value })}
                                placeholder="Any price"
                                className="w-full bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg px-3 py-2 text-sm"
                            />
                        </div>

                        {/* Min Quantity */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Min Quantity (kg)
                            </label>
                            <input
                                type="number"
                                value={filters.min_quantity}
                                onChange={(e) => setFilters({ ...filters, min_quantity: e.target.value })}
                                placeholder="Any quantity"
                                className="w-full bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg px-3 py-2 text-sm"
                            />
                        </div>

                        <button
                            onClick={() => setFilters({ crop_type: '', max_price: '', min_quantity: '' })}
                            className="text-sm text-green-600 hover:text-green-700 font-medium"
                        >
                            Reset filters
                        </button>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 p-4 lg:p-8 overflow-y-auto h-screen">
                {/* Mobile Filter Toggle */}
                <div className="lg:hidden mb-4">
                    <button
                        onClick={() => setShowFilters(true)}
                        className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-sm w-full"
                    >
                        <Filter className="w-4 h-4" />
                        <span>Filters</span>
                    </button>
                </div>

                {/* Search Bar */}
                <div className="max-w-2xl mx-auto mb-8 relative">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <input
                        type="text"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        placeholder="Search for produce, location..."
                        className="w-full pl-12 pr-4 py-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-sm focus:ring-2 focus:ring-green-500 outline-none transition-all"
                    />
                </div>

                {/* Results Grid */}
                {isLoading ? (
                    <div className="flex justify-center items-center h-64">
                        <div className="w-12 h-12 border-4 border-green-500 border-t-transparent rounded-full animate-spin" />
                    </div>
                ) : produces.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 max-w-7xl mx-auto">
                        {produces.map((produce) => (
                            <ProduceCard
                                key={produce.id}
                                produce={produce}
                                isOwner={false} // Buyer view
                                onContact={handleContactFarmer}
                            />
                        ))}
                    </div>
                ) : (
                    <div className="text-center py-16">
                        <div className="bg-gray-100 dark:bg-gray-800 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
                            <Search className="w-8 h-8 text-gray-400" />
                        </div>
                        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">No produce found</h3>
                        <p className="text-gray-500 dark:text-gray-400">
                            Try adjusting your search or filters to find what you're looking for.
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}
