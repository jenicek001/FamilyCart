import React, { useState, useEffect, useRef } from 'react';
import { 
  getSuggestedUnits, 
  getUnitSuggestions, 
  validateQuantityInput, 
  smartParseQuantity 
} from '../utils/quantity';
import { Unit, UnitCategory } from '../types/quantity';

interface QuantityInputProps {
  value: string;
  onChange: (value: string) => void;
  categoryName?: string;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
  autoFocus?: boolean;
  onBlur?: () => void;
  onKeyDown?: (e: React.KeyboardEvent) => void;
}

interface UnitSuggestion {
  id: string;
  name: string;
  symbol: string;
  category: string;
}

export const QuantityInput: React.FC<QuantityInputProps> = ({
  value,
  onChange,
  categoryName,
  placeholder = "e.g., 2 kg, 1 pack, 500 ml",
  disabled = false,
  className = "",
  autoFocus = false,
  onBlur,
  onKeyDown
}) => {
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [suggestions, setSuggestions] = useState<UnitSuggestion[]>([]);
  const [selectedSuggestion, setSelectedSuggestion] = useState(-1);
  const [inputValue, setInputValue] = useState(value);
  const [validationError, setValidationError] = useState<string | null>(null);
  
  const inputRef = useRef<HTMLInputElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);
  
  // Update internal state when prop changes
  useEffect(() => {
    setInputValue(value);
  }, [value]);
  
  // Get suggestions based on input
  useEffect(() => {
    if (inputValue.trim() === '') {
      setSuggestions(getSuggestedUnits(categoryName));
      return;
    }
    
    // Extract potential unit part for suggestions
    const parts = inputValue.trim().split(/\s+/);
    if (parts.length >= 2) {
      const lastPart = parts[parts.length - 1];
      const unitSuggestions = getUnitSuggestions(lastPart, categoryName);
      setSuggestions(unitSuggestions);
    } else {
      setSuggestions(getSuggestedUnits(categoryName));
    }
  }, [inputValue, categoryName]);
  
  // Validate input
  useEffect(() => {
    if (inputValue.trim() === '') {
      setValidationError(null);
      return;
    }
    
    const validation = validateQuantityInput(inputValue);
    setValidationError(validation.isValid ? null : validation.error || null);
  }, [inputValue]);
  
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setInputValue(newValue);
    onChange(newValue);
    setShowSuggestions(true);
    setSelectedSuggestion(-1);
  };
  
  const handleInputFocus = () => {
    setShowSuggestions(true);
    setSelectedSuggestion(-1);
  };
  
  const handleInputBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    // Delay hiding suggestions to allow clicking on them
    setTimeout(() => {
      setShowSuggestions(false);
      setSelectedSuggestion(-1);
      onBlur?.();
    }, 200);
  };
  
  const applySuggestion = (suggestion: UnitSuggestion) => {
    const parts = inputValue.trim().split(/\s+/);
    
    if (parts.length === 1 && !isNaN(parseFloat(parts[0]))) {
      // Just a number, append the unit
      const newValue = `${parts[0]} ${suggestion.symbol}`;
      setInputValue(newValue);
      onChange(newValue);
    } else if (parts.length >= 2) {
      // Replace the last part with the unit
      const newParts = [...parts.slice(0, -1), suggestion.symbol];
      const newValue = newParts.join(' ');
      setInputValue(newValue);
      onChange(newValue);
    } else {
      // Replace entire input with "1 unit"
      const newValue = `1 ${suggestion.symbol}`;
      setInputValue(newValue);
      onChange(newValue);
    }
    
    setShowSuggestions(false);
    setSelectedSuggestion(-1);
  };
  
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (showSuggestions && suggestions.length > 0) {
      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          setSelectedSuggestion(prev => 
            prev < suggestions.length - 1 ? prev + 1 : 0
          );
          break;
        case 'ArrowUp':
          e.preventDefault();
          setSelectedSuggestion(prev => 
            prev > 0 ? prev - 1 : suggestions.length - 1
          );
          break;
        case 'Enter':
          e.preventDefault();
          if (selectedSuggestion >= 0 && selectedSuggestion < suggestions.length) {
            applySuggestion(suggestions[selectedSuggestion]);
          }
          break;
        case 'Escape':
          setShowSuggestions(false);
          setSelectedSuggestion(-1);
          break;
      }
    }
    
    onKeyDown?.(e);
  };
  
  // Smart parsing indicator
  const smartParsed = smartParseQuantity(inputValue, categoryName);
  
  return (
    <div className={`quantity-input-container ${className}`}>
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          onFocus={handleInputFocus}
          onBlur={handleInputBlur}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          autoFocus={autoFocus}
          className={`
            w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
            ${validationError ? 'border-red-500' : 'border-gray-300'}
            ${disabled ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'}
          `}
        />
        
        {/* Smart parsing confidence indicator */}
        {smartParsed && smartParsed.confidence > 0.7 && (
          <div className="absolute right-2 top-2 text-green-500">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
          </div>
        )}
        
        {/* Suggestions dropdown */}
        {showSuggestions && suggestions.length > 0 && (
          <div 
            ref={suggestionsRef}
            className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-y-auto"
          >
            {suggestions.map((suggestion, index) => (
              <div
                key={suggestion.id}
                onClick={() => applySuggestion(suggestion)}
                className={`
                  px-3 py-2 cursor-pointer flex items-center justify-between hover:bg-gray-100
                  ${index === selectedSuggestion ? 'bg-blue-100' : ''}
                `}
              >
                <div>
                  <span className="font-medium">{suggestion.symbol}</span>
                  <span className="text-gray-600 ml-2">{suggestion.name}</span>
                </div>
                <span className="text-xs text-gray-400 capitalize">
                  {suggestion.category}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
      
      {/* Validation error */}
      {validationError && (
        <div className="mt-1 text-sm text-red-600">
          {validationError}
        </div>
      )}
      
      {/* Smart parsing preview */}
      {smartParsed && smartParsed.confidence > 0.5 && !validationError && (
        <div className="mt-1 text-xs text-gray-500">
          Parsed as: {smartParsed.displayText || `${smartParsed.value} ${smartParsed.unitId}`}
          {smartParsed.confidence < 0.8 && (
            <span className="ml-1 text-yellow-600">(uncertain)</span>
          )}
        </div>
      )}
    </div>
  );
};

export default QuantityInput;
