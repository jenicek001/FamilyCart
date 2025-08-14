import React from 'react';
import { ShoppingList } from '../../types';

interface ShoppingListSelectorProps {
  lists: ShoppingList[];
  currentList: ShoppingList | null;
  onSelectList: (list: ShoppingList) => void;
  onCreateList: () => void;
  user: any;
}

export function ShoppingListSelector({ 
  lists, 
  currentList, 
  onSelectList, 
  onCreateList,
}: ShoppingListSelectorProps) {
  return (
    <div className="relative flex size-full min-h-screen flex-col bg-[#FCFAF8]">
      <div className="layout-container flex h-full grow flex-col">
        {/* Header - matching Stitch design */}
        <header className="flex items-center justify-between whitespace-nowrap border-b border-solid border-b-[#F3ECE7] px-4 sm:px-6 lg:px-8 py-3 sticky top-0 z-20 bg-[#FCFAF8]/80 backdrop-blur-sm">
          <div className="flex items-center gap-3">
            <div className="size-7 text-[#ED782A]">
              <svg fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
                <path d="M44 11.2727C44 14.0109 39.8386 16.3957 33.69 17.6364C39.8386 18.877 44 21.2618 44 24C44 26.7382 39.8386 29.123 33.69 30.3636C39.8386 31.6043 44 33.9891 44 36.7273C44 40.7439 35.0457 44 24 44C12.9543 44 4 40.7439 4 36.7273C4 33.9891 8.16144 31.6043 14.31 30.3636C8.16144 29.123 4 26.7382 4 24C4 21.2618 8.16144 18.877 14.31 17.6364C8.16144 16.3957 4 14.0109 4 11.2727C4 7.25611 12.9543 4 24 4C35.0457 4 44 7.25611 44 11.2727Z" fill="currentColor"></path>
              </svg>
            </div>
            <h1 className="text-[#1B130D] text-xl font-bold leading-tight tracking-[-0.015em]">Family Groceries</h1>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={onCreateList}
              className="flex items-center justify-center overflow-hidden rounded-full h-10 w-10 bg-[#ED782A] text-white hover:bg-[#D66A25] transition-colors duration-200"
              aria-label="Add new list"
            >
              <span className="material-icons text-2xl">add</span>
            </button>
            <div className="relative group">
              <button 
                className="flex items-center justify-center overflow-hidden rounded-full h-10 w-10 bg-gray-200 text-gray-700 hover:bg-gray-300 transition-colors duration-200"
                aria-label="User menu"
              >
                <span className="material-icons text-2xl">person</span>
              </button>
            </div>
          </div>
        </header>

        {/* Main content */}
        <main className="px-4 sm:px-6 lg:px-8 flex flex-1 justify-center py-5">
          <div className="layout-content-container flex flex-col w-full max-w-4xl flex-1">
            {lists.length === 0 ? (
              /* Empty State */
              <div className="text-center py-12">
                <div className="w-24 h-24 mx-auto mb-4 bg-slate-100 rounded-full flex items-center justify-center">
                  <span className="material-icons text-4xl text-slate-400">shopping_cart</span>
                </div>
                <h3 className="text-xl font-semibold text-slate-600 mb-2">
                  No shopping lists yet
                </h3>
                <p className="text-slate-500 mb-6">
                  Create your first shopping list to get started
                </p>
                <button
                  onClick={onCreateList}
                  className="inline-flex items-center px-6 py-3 bg-[#ED782A] text-white rounded-xl hover:bg-[#D66A25] transition-colors duration-200 font-medium shadow-sm"
                >
                  <span className="material-icons text-sm mr-2">add</span>
                  Create First List
                </button>
              </div>
            ) : (
              <>
                <div className="flex items-center justify-between px-2 pb-6 pt-2">
                  <div>
                    <h2 className="text-[#1B130D] text-2xl font-bold leading-tight tracking-[-0.015em]">My Shopping Lists</h2>
                    <p className="text-gray-600 mt-1">Choose a list to start shopping</p>
                  </div>
                </div>

                {/* Shopping Lists Grid */}
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  {lists.map((list) => {
                    const pendingItems = list.items?.filter(item => !item.is_completed) || [];
                    const completedItems = list.items?.filter(item => item.is_completed) || [];
                    const totalItems = list.items?.length || 0;
                    const progressPercentage = totalItems > 0 ? Math.round((completedItems.length / totalItems) * 100) : 0;

                    return (
                      <div
                        key={list.id}
                        onClick={() => onSelectList(list)}
                        className="bg-white rounded-xl shadow-sm border border-[#F3ECE7] hover:shadow-md transition-shadow cursor-pointer p-6"
                      >
                        {/* List Header */}
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex-1 min-w-0">
                            <h3 className="font-bold text-[#1B130D] text-lg truncate mb-1">
                              {list.name}
                            </h3>
                            <p className="text-sm text-gray-600">
                              {totalItems === 0 
                                ? 'Empty list' 
                                : `${pendingItems.length} of ${totalItems} items remaining`
                              }
                            </p>
                          </div>
                          <span className="material-icons text-gray-400">chevron_right</span>
                        </div>

                        {/* Progress Bar */}
                        {totalItems > 0 && (
                          <div className="mb-4">
                            <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
                              <span>Progress</span>
                              <span>{progressPercentage}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div 
                                className="bg-[#ED782A] h-2 rounded-full transition-all duration-300"
                                style={{ width: `${progressPercentage}%` }}
                              ></div>
                            </div>
                          </div>
                        )}

                        {/* Members Preview */}
                        {list.members && list.members.length > 0 && (
                          <div className="flex items-center mb-3">
                            <span className="text-xs text-gray-500 mr-2">Shared with:</span>
                            <div className="flex items-center space-x-1">
                              {list.members.slice(0, 3).map((member, index) => (
                                <div key={member.id} className="w-6 h-6 bg-gray-300 rounded-full flex items-center justify-center">
                                  <span className="text-xs text-gray-700 font-medium">
                                    {member.full_name?.charAt(0) || member.email?.charAt(0) || 'U'}
                                  </span>
                                </div>
                              ))}
                              {list.members.length > 3 && (
                                <div className="w-6 h-6 bg-gray-200 rounded-full flex items-center justify-center">
                                  <span className="text-xs text-gray-600">
                                    +{list.members.length - 3}
                                  </span>
                                </div>
                              )}
                            </div>
                          </div>
                        )}

                        {/* Quick Actions */}
                        <div className="pt-4 border-t border-gray-100">
                          <div className="flex items-center justify-between text-xs text-gray-500">
                            <span>Last updated: {new Date(list.updated_at).toLocaleDateString()}</span>
                            <button 
                              onClick={(e) => {
                                e.stopPropagation();
                                // Add list options menu here
                              }}
                              className="p-1 hover:bg-gray-100 rounded"
                            >
                              <span className="material-icons text-sm">more_vert</span>
                            </button>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
