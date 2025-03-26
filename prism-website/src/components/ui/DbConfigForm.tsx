"use client";

import React, { useState, useEffect } from 'react';
import AnimatedButton from './AnimatedButton';

interface DbConfig {
  user: string;
  password: string;
  host: string;
  port: string;
  database: string;
}

interface DbConfigFormProps {
  onSave: (config: DbConfig) => void;
  initialConfig?: DbConfig;
}

export default function DbConfigForm({ onSave, initialConfig }: DbConfigFormProps) {
  const [config, setConfig] = useState<DbConfig>({
    user: '',
    password: '',
    host: '',
    port: '5432',
    database: '',
  });

  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (initialConfig) {
      setConfig(initialConfig);
    }
  }, [initialConfig]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setConfig(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(config);
    setIsVisible(false);
  };

  return (
    <div className="mb-8">
      <div className="flex justify-end">
        <AnimatedButton
          onClick={() => setIsVisible(!isVisible)}
          className="w-auto px-6"
        >
          {isVisible ? 'Close Config' : 'DB Config'}
        </AnimatedButton>
      </div>

      {isVisible && (
        <div className="mt-4 p-6 bg-nova-gray6/70 backdrop-blur rounded-md">
          <h3 className="text-xl mb-4 font-light">Database Configuration</h3>
          <form onSubmit={handleSubmit}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="block text-sm">Host</label>
                <input
                  type="text"
                  name="host"
                  value={config.host}
                  onChange={handleChange}
                  className="w-full p-2 bg-nova-gray4/50 border border-nova-gray5 rounded text-white"
                  placeholder="localhost"
                />
              </div>
              <div className="space-y-2">
                <label className="block text-sm">Port</label>
                <input
                  type="text"
                  name="port"
                  value={config.port}
                  onChange={handleChange}
                  className="w-full p-2 bg-nova-gray4/50 border border-nova-gray5 rounded text-white"
                  placeholder="5432"
                />
              </div>
              <div className="space-y-2">
                <label className="block text-sm">Database</label>
                <input
                  type="text"
                  name="database"
                  value={config.database}
                  onChange={handleChange}
                  className="w-full p-2 bg-nova-gray4/50 border border-nova-gray5 rounded text-white"
                  placeholder="leaderboard"
                />
              </div>
              <div className="space-y-2">
                <label className="block text-sm">User</label>
                <input
                  type="text"
                  name="user"
                  value={config.user}
                  onChange={handleChange}
                  className="w-full p-2 bg-nova-gray4/50 border border-nova-gray5 rounded text-white"
                  placeholder="postgres"
                />
              </div>
              <div className="space-y-2 md:col-span-2">
                <label className="block text-sm">Password</label>
                <input
                  type="password"
                  name="password"
                  value={config.password}
                  onChange={handleChange}
                  className="w-full p-2 bg-nova-gray4/50 border border-nova-gray5 rounded text-white"
                  placeholder="********"
                />
              </div>
            </div>
            <div className="mt-6 flex justify-end">
              <AnimatedButton
                className="w-auto px-6"
                onClick={handleSubmit}
              >
                Save
              </AnimatedButton>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
