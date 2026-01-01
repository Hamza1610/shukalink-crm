/**
 * Produce Card Component
 * Reusable card for both Farmer (Edit/Delete) and Buyer (View/Contact) views
 */
'use client';

import { Edit, Trash2, MessageCircle, MapPin } from 'lucide-react';

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

interface ProduceCardProps {
    produce: Produce;
    isOwner?: boolean;
    onEdit?: (produce: Produce) => void;
    onDelete?: (id: string) => void;
    onContact?: (produce: Produce) => void;
}

export default function ProduceCard({
    produce,
    isOwner = false,
    onEdit,
    onDelete,
    onContact
}: ProduceCardProps) {

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

    const imageUrl = produce.images && produce.images.length > 0
        ? `http://localhost:8000${produce.images[0]}`
        : null;

    return (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow border border-gray-100 dark:border-gray-700 flex flex-col h-full">
            {/* Image Header */}
            <div className="relative h-48 bg-gray-100 dark:bg-gray-700">
                {imageUrl ? (
                    <img
                        src={imageUrl}
                        alt={produce.crop_type}
                        className="w-full h-full object-cover"
                    />
                ) : (
                    <div className="w-full h-full flex items-center justify-center bg-green-50 dark:bg-green-900/20">
                        <span className="text-4xl">🌾</span>
                    </div>
                )}

                <div className="absolute top-3 right-3">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium shadow-sm backdrop-blur-md ${getStatusColor(produce.status)}`}>
                        {produce.status}
                    </span>
                </div>

                <div className="absolute bottom-0 left-0 right-0 p-3 bg-gradient-to-t from-black/60 to-transparent">
                    <h3 className="text-lg font-bold text-white shadow-sm">
                        {produce.crop_type}
                    </h3>
                </div>
            </div>

            {/* Card Body */}
            <div className="p-4 flex-grow flex flex-col">
                <div className="flex justify-between items-baseline mb-4">
                    {/* <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                        ₦{produce.price_per_kg.toLocaleString()}
                        <span className="text-sm font-normal text-gray-500 dark:text-gray-400">/kg</span>
                    </p>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                        {produce.quantity_kg.toLocaleString()} kg
                    </p> */}
                </div>

                <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400 mb-6 flex-grow">
                    <p className="flex items-center gap-2">
                        <span className="font-medium">Harvest:</span>
                        {new Date(produce.harvest_date).toLocaleDateString()}
                    </p>
                    {produce.location && (
                        <p className="flex items-center gap-2">
                            <MapPin className="w-4 h-4 text-gray-400" />
                            {produce.location}
                        </p>
                    )}
                    {produce.quality_indicators && produce.quality_indicators.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-2">
                            {produce.quality_indicators.map((tag, idx) => (
                                <span key={idx} className="text-xs bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 px-2 py-0.5 rounded-full">
                                    {tag}
                                </span>
                            ))}
                        </div>
                    )}
                </div>

                {/* Actions */}
                <div className="pt-4 border-t border-gray-100 dark:border-gray-700 mt-auto">
                    {isOwner ? (
                        <div className="flex gap-2">
                            <button
                                onClick={() => onEdit?.(produce)}
                                className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-blue-50 hover:bg-blue-100 dark:bg-blue-900/30 dark:hover:bg-blue-900/50 text-blue-700 dark:text-blue-300 rounded-lg transition-colors text-sm font-medium"
                            >
                                <Edit className="w-4 h-4" />
                                Edit
                            </button>
                            <button
                                onClick={() => onDelete?.(produce.id)}
                                className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-red-50 hover:bg-red-100 dark:bg-red-900/30 dark:hover:bg-red-900/50 text-red-700 dark:text-red-300 rounded-lg transition-colors text-sm font-medium"
                            >
                                <Trash2 className="w-4 h-4" />
                                Delete
                            </button>
                        </div>
                    ) : (
                        <button
                            onClick={() => onContact?.(produce)}
                            className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors text-sm font-medium shadow-sm"
                        >
                            <MessageCircle className="w-4 h-4" />
                            Contact Farmer
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
}
