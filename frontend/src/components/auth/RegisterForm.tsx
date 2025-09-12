"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Alert } from "@/components/ui/alert";
import { useAuth } from "@/contexts/AuthContext";

interface RegisterFormProps {
  onSuccess?: () => void;
}

export function RegisterForm({ onSuccess }: RegisterFormProps) {
  const { register } = useAuth();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    firstName: "",
    lastName: "",
    company: "",
    phone: "",
    role: "public" as "public" | "developer" | "investor" | "admin",
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    try {
      await register(formData);
      onSuccess?.();
    } catch {
      setError("Registration failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <Alert className="bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800 text-red-800 dark:text-red-200">
          {error}
        </Alert>
      )}

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="firstName" className="text-sm font-medium text-gray-700 dark:text-gray-300">
            First Name
          </Label>
          <Input
            id="firstName"
            name="firstName"
            value={formData.firstName}
            onChange={handleChange}
            required
            className="w-full"
            placeholder="John"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="lastName" className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Last Name
          </Label>
          <Input
            id="lastName"
            name="lastName"
            value={formData.lastName}
            onChange={handleChange}
            required
            className="w-full"
            placeholder="Doe"
          />
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="email" className="text-sm font-medium text-gray-700 dark:text-gray-300">
          Email
        </Label>
        <Input
          id="email"
          name="email"
          type="email"
          value={formData.email}
          onChange={handleChange}
          required
          className="w-full"
          placeholder="john@example.com"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="password" className="text-sm font-medium text-gray-700 dark:text-gray-300">
          Password
        </Label>
        <Input
          id="password"
          name="password"
          type="password"
          value={formData.password}
          onChange={handleChange}
          required
          className="w-full"
          placeholder="Create a password"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="role" className="text-sm font-medium text-gray-700 dark:text-gray-300">
          Role
        </Label>
        <Select
          name="role"
          value={formData.role}
          onValueChange={(value) => setFormData(prev => ({ ...prev, role: value as "public" | "developer" | "investor" | "admin" }))}
        >
          <option value="public">Public User</option>
          <option value="developer">Developer</option>
          <option value="investor">Investor</option>
          <option value="admin">Admin</option>
        </Select>
      </div>

      <div className="space-y-2">
        <Label htmlFor="company" className="text-sm font-medium text-gray-700 dark:text-gray-300">
          Company (Optional)
        </Label>
        <Input
          id="company"
          name="company"
          value={formData.company}
          onChange={handleChange}
          className="w-full"
          placeholder="Your company name"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="phone" className="text-sm font-medium text-gray-700 dark:text-gray-300">
          Phone (Optional)
        </Label>
        <Input
          id="phone"
          name="phone"
          value={formData.phone}
          onChange={handleChange}
          className="w-full"
          placeholder="+1 (555) 123-4567"
        />
      </div>

      <Button
        type="submit"
        disabled={isLoading}
        className="w-full bg-blue-600 hover:bg-blue-700 text-white"
      >
        {isLoading ? "Creating account..." : "Create Account"}
      </Button>
    </form>
  );
}