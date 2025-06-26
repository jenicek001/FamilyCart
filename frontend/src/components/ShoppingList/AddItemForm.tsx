import React, { useState } from 'react';
import { Item } from '../../types';
import { getAllCategories, inferCategory } from '../../utils/categories';

interface AddItemFormProps {
  onSubmit: (item: Omit<Item, 'id' | 'created_at' | 'updated_at' | 'shopping_list_id'>) => Promise<void>;
  onCancel: () => void;
}

export function AddItemForm({ onSubmit, onCancel }: AddItemFormProps) {
  const [name, setName] = useState('');
  const [quantity, setQuantity] = useState(1);
  const [category, setCategory] = useState('');
  const [notes, setNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const allCategories = getAllCategories();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setIsSubmitting(true);
    try {
      const finalCategory = category || inferCategory(name);
      await onSubmit({
        name: name.trim(),
        quantity: quantity || 1,
        category: { 
          id: 0, // This will be handled by the backend
          name: finalCategory 
        },
        notes: notes.trim() || null,
        is_completed: false,
        owner_id: 0, // This will be set by the backend
        category_id: null,
        description: null,
        icon_name: null
      });
      
      // Reset form
      setName('');
      setQuantity(1);
      setCategory('');
      setNotes('');
    } catch (error) {
      console.error('Failed to add item:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      onCancel();
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-soft border border-slate-200 p-6 animate-slide-up">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-slate-900">Add New Item</h3>
        <button
          onClick={onCancel}
          className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-50 rounded-lg transition-colors"
        >
          <span className="material-icons text-sm">close</span>
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Item Name */}
        <div>
          <label htmlFor="item-name" className="block text-sm font-medium text-slate-700 mb-2">
            Item Name *
          </label>
          <input
            id="item-name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Enter item name"
            className="w-full px-3 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
            required
            autoFocus
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Quantity */}
          <div>
            <label htmlFor="item-quantity" className="block text-sm font-medium text-slate-700 mb-2">
              Quantity
            </label>
            <input
              id="item-quantity"
              type="number"
              value={quantity}
              onChange={(e) => setQuantity(parseInt(e.target.value) || 1)}
              onKeyDown={handleKeyPress}
              min="1"
              className="w-full px-3 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
            />
          </div>

          {/* Category */}
          <div>
            <label htmlFor="item-category" className="block text-sm font-medium text-slate-700 mb-2">
              Category
            </label>
            <select
              id="item-category"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              onKeyDown={handleKeyPress}
              className="w-full px-3 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
            >
              <option value="">Auto-detect</option>
              {allCategories.map((cat) => (
                <option key={cat.name} value={cat.name.toLowerCase()}>
                  {cat.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Notes */}
        <div>
          <label htmlFor="item-notes" className="block text-sm font-medium text-slate-700 mb-2">
            Notes (Optional)
          </label>
          <textarea
            id="item-notes"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Add any additional notes..."
            rows={2}
            className="w-full px-3 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors resize-none"
          />
        </div>

        {/* Preview */}
        {name && (
          <div className="bg-slate-50 rounded-lg p-3 border border-slate-200">
            <p className="text-sm text-slate-600 mb-2">Preview:</p>
            <div className="flex items-center">
              <div className="w-8 h-8 rounded-lg bg-primary-100 flex items-center justify-center mr-3">
                <span className="material-icons text-primary-600 text-sm">
                  {allCategories.find(c => c.name.toLowerCase() === (category || inferCategory(name)))?.icon || 'category'}
                </span>
              </div>
              <div>
                <p className="font-medium text-slate-900">
                  {name}
                  {quantity > 1 && (
                    <span className="ml-2 px-2 py-0.5 bg-slate-200 text-slate-600 text-xs rounded-full">
                      {quantity}
                    </span>
                  )}
                </p>
                <p className="text-sm text-slate-500 capitalize">
                  {category || inferCategory(name)}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-end space-x-3 pt-2">
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2.5 text-slate-600 hover:text-slate-800 hover:bg-slate-50 rounded-lg transition-colors font-medium"
            disabled={isSubmitting}
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={!name.trim() || isSubmitting}
            className="inline-flex items-center px-6 py-2.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium shadow-soft"
          >
            {isSubmitting ? (
              <>
                <span className="animate-spin mr-2">⏳</span>
                Adding...
              </>
            ) : (
              <>
                <span className="material-icons text-sm mr-2">add</span>
                Add Item
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
