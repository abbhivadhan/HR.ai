'use client'

import { useState } from 'react'
import { supabase, supabaseAuth } from '@/lib/supabase'

export default function TestRegistrationPage() {
  const [email, setEmail] = useState('test@example.com')
  const [password, setPassword] = useState('Password123!')
  const [firstName, setFirstName] = useState('Test')
  const [lastName, setLastName] = useState('User')
  const [userType, setUserType] = useState<'CANDIDATE' | 'COMPANY'>('CANDIDATE')
  const [logs, setLogs] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const addLog = (message: string, type: 'info' | 'success' | 'error' = 'info') => {
    const timestamp = new Date().toLocaleTimeString()
    const prefix = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'
    setLogs(prev => [...prev, `[${timestamp}] ${prefix} ${message}`])
  }

  const clearLogs = () => setLogs([])

  const testConnection = async () => {
    clearLogs()
    addLog('Testing Supabase connection...')
    try {
      const { data, error } = await supabase.auth.getSession()
      if (error) {
        addLog(`Connection error: ${error.message}`, 'error')
      } else {
        addLog('Connection successful!', 'success')
      }
    } catch (err: any) {
      addLog(`Exception: ${err.message}`, 'error')
    }
  }

  const testTables = async () => {
    clearLogs()
    addLog('Testing database tables...')
    
    try {
      const { data, error } = await supabase
        .from('users')
        .select('count')
        .limit(1)
      
      if (error) {
        addLog(`Users table error: ${error.message}`, 'error')
        addLog(`Error code: ${error.code}`, 'error')
        addLog(`Error details: ${error.details}`, 'error')
      } else {
        addLog('Users table exists and is accessible!', 'success')
      }
    } catch (err: any) {
      addLog(`Exception: ${err.message}`, 'error')
    }
  }

  const testRegistration = async () => {
    clearLogs()
    setIsLoading(true)
    
    try {
      addLog(`Starting registration for: ${email}`)
      
      // Step 1: Auth signup
      addLog('Step 1: Creating auth user...')
      const { data: authData, error: authError } = await supabaseAuth.signUp(
        email,
        password,
        {
          first_name: firstName,
          last_name: lastName,
          user_type: userType
        }
      )

      if (authError) {
        addLog(`Auth error: ${authError.message}`, 'error')
        addLog(`Full error: ${JSON.stringify(authError)}`, 'error')
        return
      }

      if (!authData.user) {
        addLog('No user returned from signup', 'error')
        return
      }

      addLog(`Auth user created! ID: ${authData.user.id}`, 'success')

      // Step 2: Create profile
      addLog('Step 2: Creating user profile...')
      await new Promise(resolve => setTimeout(resolve, 500))

      const profileData = {
        id: authData.user.id,
        email: email,
        first_name: firstName,
        last_name: lastName,
        user_type: userType,
        is_active: true,
        is_verified: false,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }

      addLog(`Profile data: ${JSON.stringify(profileData, null, 2)}`)

      const { data: insertData, error: profileError } = await supabase
        .from('users')
        .insert(profileData)
        .select()

      if (profileError) {
        addLog(`Profile error: ${profileError.message}`, 'error')
        addLog(`Error code: ${profileError.code}`, 'error')
        addLog(`Error hint: ${profileError.hint}`, 'error')
        addLog(`Error details: ${profileError.details}`, 'error')
        addLog(`Full error: ${JSON.stringify(profileError, null, 2)}`, 'error')
        return
      }

      addLog('Profile created successfully!', 'success')
      addLog(`Profile data: ${JSON.stringify(insertData, null, 2)}`, 'success')
      addLog('🎉 Registration completed!', 'success')

    } catch (err: any) {
      addLog(`Exception: ${err.message}`, 'error')
      addLog(`Stack: ${err.stack}`, 'error')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Registration Debug Tool</h1>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Test Data</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 border rounded"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3 py-2 border rounded"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">First Name</label>
              <input
                type="text"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                className="w-full px-3 py-2 border rounded"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Last Name</label>
              <input
                type="text"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                className="w-full px-3 py-2 border rounded"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">User Type</label>
              <select
                value={userType}
                onChange={(e) => setUserType(e.target.value as 'CANDIDATE' | 'COMPANY')}
                className="w-full px-3 py-2 border rounded"
              >
                <option value="CANDIDATE">Candidate</option>
                <option value="COMPANY">Company</option>
              </select>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Tests</h2>
          <div className="flex gap-4">
            <button
              onClick={testConnection}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              1. Test Connection
            </button>
            <button
              onClick={testTables}
              className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
            >
              2. Test Tables
            </button>
            <button
              onClick={testRegistration}
              disabled={isLoading}
              className="px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600 disabled:opacity-50"
            >
              {isLoading ? 'Testing...' : '3. Test Registration'}
            </button>
            <button
              onClick={clearLogs}
              className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
            >
              Clear Logs
            </button>
          </div>
        </div>

        <div className="bg-gray-900 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4 text-white">Console Logs</h2>
          <div className="bg-black rounded p-4 h-96 overflow-y-auto font-mono text-sm">
            {logs.length === 0 ? (
              <div className="text-gray-500">No logs yet. Click a test button above.</div>
            ) : (
              logs.map((log, index) => (
                <div
                  key={index}
                  className={`mb-1 ${
                    log.includes('✅') ? 'text-green-400' :
                    log.includes('❌') ? 'text-red-400' :
                    'text-gray-300'
                  }`}
                >
                  {log}
                </div>
              ))
            )}
          </div>
        </div>

        <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h3 className="font-semibold text-yellow-800 mb-2">Instructions:</h3>
          <ol className="list-decimal list-inside text-sm text-yellow-700 space-y-1">
            <li>Click "1. Test Connection" to verify Supabase is reachable</li>
            <li>Click "2. Test Tables" to check if the users table exists</li>
            <li>Click "3. Test Registration" to see exactly where registration fails</li>
            <li>Copy any error messages and share them for debugging</li>
          </ol>
        </div>
      </div>
    </div>
  )
}
