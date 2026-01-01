import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { X, Upload, Loader2, Check } from 'lucide-react';
import { apiClient } from '@/lib/api';
import ImageUpload from './ImageUpload';

interface ProduceFormData {
    crop_type: string;
    quantity_kg: number;
    price_per_kg: number;
    harvest_date: string;
    quality_indicators?: string;
    description?: string;
    location?: string;
}

interface ProduceFormProps {
    onClose: () => void;
    onSuccess: () => void;
    initialData?: any;
}

export default function ProduceForm({ onClose, onSuccess, initialData }: ProduceFormProps) {
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [image, setImage] = useState<File | null>(null);

    const { register, handleSubmit, reset, formState: { errors } } = useForm<ProduceFormData>({
        defaultValues: initialData ? {
            ...initialData,
            harvest_date: new Date(initialData.harvest_date).toISOString().split('T')[0]
        } : {
            harvest_date: new Date().toISOString().split('T')[0],
            location: ''
        }
    });

    // Reset form when initialData changes (fixes edit mode issue)
    useEffect(() => {
        if (initialData) {
            reset({
                ...initialData,
                harvest_date: new Date(initialData.harvest_date).toISOString().split('T')[0]
            });
        } else {
            reset({
                crop_type: '',
                quantity_kg: 0,
                price_per_kg: 0,
                harvest_date: new Date().toISOString().split('T')[0],
                quality_indicators: '',
                description: '',
                location: ''
            });
        }
    }, [initialData, reset]);

    const onSubmit = async (data: ProduceFormData) => {
        setIsSubmitting(true);
        setError(null);

        try {
            // Transform data types
            const payload = {
                ...data,
                quantity_kg: Number(data.quantity_kg),
                price_per_kg: Number(data.price_per_kg),
                quality_indicators: data.quality_indicators ? data.quality_indicators.split(',').map(s => s.trim()) : [],
            };

            const token = localStorage.getItem('auth_token');
            const url = initialData
                ? `http://localhost:8000/api/v1/produce/${initialData.id}`
                : 'http://localhost:8000/api/v1/produce/';

            const method = initialData ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method,
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Failed to save produce');
            }

            const dataToUse = initialData || await response.json();
            const produceId = dataToUse.id;

            // Handle image upload
            if (image) {
                const formData = new FormData();
                formData.append('file', image);

                const uploadResponse = await fetch(`http://localhost:8000/api/v1/produce/${produceId}/image`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    },
                    body: formData
                });

                if (!uploadResponse.ok) {
                    console.warn('Image upload failed');
                    // Don't fail the whole submission if image fails, just warn
                }
            }

            onSuccess();
            onClose();
        } catch (err: any) {
            console.error('Submit error:', err);
            setError(err.message || 'An error occurred');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center p-4 z-50 backdrop-blur-sm">
            <div className="bg-white dark:bg-gray-800 rounded-2xl w-full max-w-lg shadow-2xl flex flex-col max-h-[90vh]">
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-gray-100 dark:border-gray-700">
                    <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                        {initialData ? 'Edit Produce' : 'Add New Produce'}
                    </h2>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition-colors"
                    >
                        <X className="w-5 h-5 text-gray-500" />
                    </button>
                </div>

                {/* Form */}
                <div className="overflow-y-auto p-6">
                    {error && (
                        <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl text-sm text-red-600 dark:text-red-400">
                            {error}
                        </div>
                    )}

                    <form id="produce-form" onSubmit={handleSubmit(onSubmit)} className="space-y-5">
                        {/* Crop Type */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                Crop Type
                            </label>
                            <select
                                {...register('crop_type', { required: 'Crop type is required' })}
                                className="w-full px-4 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-green-500 outline-none transition-all"
                            >
                                <option value="">Select crop...</option>
                                <option value="Maize">Maize</option>
                                <option value="Rice">Rice</option>
                                <option value="Tomatoes">Tomatoes</option>
                                <option value="Beans">Beans</option>
                                <option value="Cassava">Cassava</option>
                                <option value="Yam">Yam</option>
                                <option value="Sorghum">Sorghum</option>
                                <option value="Soybeans">Soybeans</option>
                                <option value="Onions">Onions</option>
                                <option value="Peppers">Peppers</option>
                            </select>
                            {errors.crop_type && (
                                <p className="mt-1 text-xs text-red-500">{errors.crop_type.message}</p>
                            )}
                        </div>

                        <div className="grid grid-cols-2 gap-5">
                            {/* Quantity */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                    Quantity (kg)
                                </label>
                                <input
                                    type="number"
                                    step="0.01"
                                    {...register('quantity_kg', { required: 'Quantity is required', min: 0 })}
                                    className="w-full px-4 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-green-500 outline-none transition-all"
                                    placeholder="0"
                                />
                                {errors.quantity_kg && (
                                    <p className="mt-1 text-xs text-red-500">{errors.quantity_kg.message}</p>
                                )}
                            </div>

                            {/* Price */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                    Price per kg (₦)
                                </label>
                                <input
                                    type="number"
                                    step="0.01"
                                    {...register('price_per_kg', { required: 'Price is required', min: 0 })}
                                    className="w-full px-4 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-green-500 outline-none transition-all"
                                    placeholder="0.00"
                                />
                                {errors.price_per_kg && (
                                    <p className="mt-1 text-xs text-red-500">{errors.price_per_kg.message}</p>
                                )}
                            </div>
                        </div>

                        {/* Location */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                Location
                            </label>
                            <input
                                type="text"
                                {...register('location', { required: 'Location is required' })}
                                className="w-full px-4 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-green-500 outline-none transition-all"
                                placeholder="e.g. Kano, Nigeria"
                            />
                            {errors.location && (
                                <p className="mt-1 text-xs text-red-500">{errors.location.message}</p>
                            )}
                        </div>

                        {/* Harvest Date */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                Harvest Date
                            </label>
                            <input
                                type="date"
                                {...register('harvest_date', { required: 'Harvest date is required' })}
                                className="w-full px-4 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-green-500 outline-none transition-all"
                            />
                            {errors.harvest_date && (
                                <p className="mt-1 text-xs text-red-500">{errors.harvest_date.message}</p>
                            )}
                        </div>

                        {/* Quality Indicators */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                Quality details (optional)
                            </label>
                            <input
                                type="text"
                                {...register('quality_indicators')}
                                className="w-full px-4 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-green-500 outline-none transition-all"
                                placeholder="e.g. Organic, Grade A, Fresh check (comma separated)"
                            />
                        </div>

                        {/* Image Upload */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Produce Image (Optional)
                            </label>
                            <ImageUpload
                                onImageSelect={(file) => setImage(file)}
                                currentImage={initialData?.image_url || ((initialData?.images && initialData.images.length > 0) ? initialData.images[0] : null)}
                            />
                        </div>
                    </form>
                </div>

                {/* Footer */}
                <div className="p-6 border-t border-gray-100 dark:border-gray-700 flex justify-end gap-3">
                    <button
                        onClick={onClose}
                        type="button"
                        disabled={isSubmitting}
                        className="px-5 py-2.5 rounded-xl font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                    >
                        Cancel
                    </button>
                    <button
                        type="submit"
                        form="produce-form"
                        disabled={isSubmitting}
                        className="px-5 py-2.5 rounded-xl font-medium bg-green-600 hover:bg-green-700 text-white shadow-lg hover:shadow-green-500/25 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                        {isSubmitting ? (
                            <>
                                <Loader2 className="w-4 h-4 animate-spin" />
                                Saving...
                            </>
                        ) : (
                            <>
                                <Check className="w-4 h-4" />
                                Save Produce
                            </>
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
}
