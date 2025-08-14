"use client";

import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { useState } from "react";

interface ConfirmDeleteDialogProps {
  open: boolean;
  onConfirm: () => void;
  onCancel: () => void;
  listName?: string;
}

export default function ConfirmDeleteDialog({ open, onConfirm, onCancel, listName }: ConfirmDeleteDialogProps) {
  return (
    <Dialog open={open} onOpenChange={open => !open && onCancel()}>
      <DialogContent className="max-w-md mx-4 sm:mx-0 p-4 sm:p-6">
        <DialogHeader className="pb-2 sm:pb-4">
          <DialogTitle className="text-lg sm:text-xl">Delete Shopping List?</DialogTitle>
        </DialogHeader>
        <div className="py-2 text-sm sm:text-base">
          Are you sure you want to delete <b>{listName || "this shopping list"}</b>? This action cannot be undone.
        </div>
        <DialogFooter className="pt-2 sm:pt-4 flex-col sm:flex-row gap-2">
          <Button variant="outline" onClick={onCancel} className="w-full sm:w-auto">Cancel</Button>
          <Button variant="destructive" onClick={onConfirm} className="w-full sm:w-auto">Delete</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
