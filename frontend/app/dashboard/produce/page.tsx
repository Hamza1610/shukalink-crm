/**
 * Farmer Produce Management Page
 * List, create, edit, and delete produce listings
 */
'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { Plus, Package, Edit, Trash2, AlertCircle } from 'lucide-react';
import ProduceForm from '@/components/ProduceForm';
import ProduceCard from '@/components/ProduceCard';

interface Produce {
    id: string;
    crop_type: string;
    quantity_kg: number;
    price_per_kg: number;
    harvest_date: string;
    status: 'available' | 'reserved' | 'sold';
    quality_indicators?: string[];
    created_at: string;
}

export default function ProducePage() {
    const { user } = useAuth();
    const [produces, setProduces] = useState<Produce[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showForm, setShowForm] = useState(false);

    const [selectedProduce, setSelectedProduce] = useState<Produce | null>(null);

    useEffect(() => {
        fetchProduces();
    }, [user]);

    const fetchProduces = async () => {
        if (!user) return;

        setIsLoading(true);
        setError(null);

        try {
            const token = localStorage.getItem('auth_token');
            const response = await fetch(
                `http://localhost:8000/api/v1/produce/all?farmer_id=${user.id}`,
                {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                }
            );

            if (response.ok) {
                const data = await response.json();
                setProduces(data);
            } else {
                throw new Error('Failed to fetch produce');
            }
        } catch (err) {
            setError('Failed to load produce listings');
            console.error('Error fetching produce:', err);
        } finally {
            setIsLoading(false);
        }
    };

    const handleDelete = async (produceId: string) => {
        if (!confirm('Are you sure you want to delete this produce listing?')) {
            return;
        }

        try {
            const token = localStorage.getItem('auth_token');
            const response = await fetch(
                `http://localhost:8000/api/v1/produce/${produceId}`,
                {
                    method: 'DELETE',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                }
            );

            if (response.ok) {
                setProduces(produces.filter(p => p.id !== produceId));
            } else {
                alert('Failed to delete produce');
            }
        } catch (err) {
            console.error('Error deleting produce:', err);
            alert('Failed to delete produce');
        }
    };

    const handleEdit = (produce: Produce) => {
        setSelectedProduce(produce);
        setShowForm(true);
    };

    const handleFormClose = () => {
        setShowForm(false);
        setSelectedProduce(null);
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'available':
                return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300';
            case 'reserved':
                return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300';
            case 'sold':
                return 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300';
            default:
                return 'bg-gray-100 text-gray-800';
        }
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-center">
                    <div className="w-16 h-16 border-4 border-green-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                    <p className="text-gray-600 dark:text-gray-400">Loading produce...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="p-6">
            {/* Header */}
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                        My Produce
                    </h1>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        Manage your crop listings
                    </p>
                </div>
                <button
                    onClick={() => {
                        setSelectedProduce(null);
                        setShowForm(true);
                    }}
                    className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-colors"
                >
                    <Plus className="w-5 h-5" />
                    Add Produce
                </button>
            </div>

            {/* Error Message */}
            {error && (
                <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-center gap-3">
                    <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400" />
                    <p className="text-red-800 dark:text-red-200">{error}</p>
                </div>
            )}

            {/* Empty State */}
            {produces.length === 0 && !error && (
                <div className="text-center py-12">
                    <Package className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                        No produce listings yet
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400 mb-6">
                        Start by adding your first crop listing
                    </p>
                    <button
                        onClick={() => {
                            setSelectedProduce(null);
                            setShowForm(true);
                        }}
                        className="inline-flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-colors"
                    >
                        <Plus className="w-5 h-5" />
                        Add Your First Produce
                    </button>
                </div>
            )}

            {/* Produce Grid */}
            {produces.length > 0 && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {produces.map((produce) => (
                        <ProduceCard
                            key={produce.id}
                            produce={produce}
                            isOwner={true}
                            onEdit={() => handleEdit(produce)}
                            onDelete={handleDelete}
                        />
                    ))}
                </div>
            )}

            {/* Produce Form Modal */}
            {showForm && (
                <ProduceForm
                    onClose={handleFormClose}
                    onSuccess={() => {
                        fetchProduces();
                        handleFormClose();
                    }}
                    initialData={selectedProduce}
                />
            )}
        </div>
    );
}
