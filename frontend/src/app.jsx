import React, { useState, useEffect } from 'react';
import { Toaster } from 'react-hot-toast';
import { 
  MessageSquare, 
  Calendar, 
  BarChart3, 
  Send, 
  Settings,
  Menu,
  X
} from 'lucide-react';

import CreateMessage from './components/CreateMessage';
import MessageList from './components/MessageList';
import MessageDetails from './components/MessageDetails';
import Dashboard from './components/Dashboard';
import TestMessage from './components/TestMessage';
import { apiService } from './api';

const App = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedMessageId, setSelectedMessageId] = useState(null);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [apiStatus, setApiStatus] = useState(null);

  // Verificar estado de la API al cargar
  useEffect(() => {
    const checkAPIStatus = async () => {
      try {
        const status = await apiService.checkHealth();
        setApiStatus(status);
      } catch (error) {
        setApiStatus({ success: false, message: 'API no disponible' });
      }
    };

    checkAPIStatus();
    // Verificar cada 30 segundos
    const interval = setInterval(checkAPIStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const navigation = [
    { 
      id: 'dashboard', 
      name: 'Dashboard', 
      icon: BarChart3,
      description: 'Resumen y estadísticas'
    },
    { 
      id: 'create', 
      name: 'Nuevo Mensaje', 
      icon: MessageSquare,
      description: 'Programar mensaje'
    },
    { 
      id: 'list', 
      name: 'Mensajes', 
      icon: Calendar,
      description: 'Ver mensajes programados'
    },
    { 
      id: 'test', 
      name: 'Envío Directo', 
      icon: Send,
      description: 'Enviar mensaje inmediato'
    }
  ];

  const handleTabChange = (tabId) => {
    setActiveTab(tabId);
    setSelectedMessageId(null);
    setIsMobileMenuOpen(false);
  };

  const handleEditMessage = (messageId) => {
    setSelectedMessageId(messageId);
    setActiveTab('edit');
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      
      case 'create':
        return (
          <CreateMessage 
            onSuccess={() => setActiveTab('list')}
          />
        );
      
      case 'list':
        return (
          <MessageList 
            onEditMessage={handleEditMessage}
          />
        );
      
      case 'edit':
        return selectedMessageId ? (
          <MessageDetails 
            messageId={selectedMessageId}
            onClose={() => setActiveTab('list')}
            onDeleted={() => setActiveTab('list')}
          />
        ) : (
          <div className="text-center py-8">
            <p className="text-gray-500">Selecciona un mensaje para editar</p>
          </div>
        );
      
      case 'test':
        return <TestMessage />;
      
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Toast notifications */}
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            iconTheme: {
              primary: '#22c55e',
              secondary: '#fff',
            },
          },
          error: {
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />

      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo y título */}
            <div className="flex items-center space-x-3">
              <div className="flex-shrink-0 bg-whatsapp-500 p-2 rounded-lg">
                <MessageSquare className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  WhatsApp Scheduler
                </h1>
                <p className="text-xs text-gray-500 hidden sm:block">
                  Programa tus mensajes de WhatsApp
                </p>
              </div>
            </div>

            {/* Status indicator */}
            <div className="hidden sm:flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${
                  apiStatus?.success ? 'bg-green-500' : 'bg-red-500'
                }`} />
                <span className="text-sm text-gray-600">
                  {apiStatus?.success ? 'API Conectada' : 'API Desconectada'}
                </span>
              </div>
              
              {apiStatus?.data?.whatsapp_configured && (
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 rounded-full bg-whatsapp-500" />
                  <span className="text-sm text-gray-600">WhatsApp OK</span>
                </div>
              )}
            </div>

            {/* Mobile menu button */}
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="sm:hidden p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100"
            >
              {isMobileMenuOpen ? (
                <X className="h-6 w-6" />
              ) : (
                <Menu className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex flex-col sm:flex-row gap-6">
          {/* Sidebar Navigation */}
          <nav className={`
            w-full sm:w-64 bg-white rounded-lg shadow-sm p-4
            ${isMobileMenuOpen ? 'block' : 'hidden sm:block'}
          `}>
            <div className="space-y-2">
              {navigation.map((item) => {
                const Icon = item.icon;
                return (
                  <button
                    key={item.id}
                    onClick={() => handleTabChange(item.id)}
                    className={`
                      w-full flex items-center space-x-3 px-3 py-3 rounded-lg text-left transition-colors
                      ${activeTab === item.id 
                        ? 'bg-whatsapp-50 text-whatsapp-700 border border-whatsapp-200' 
                        : 'text-gray-700 hover:bg-gray-50'
                      }
                    `}
                  >
                    <Icon className="h-5 w-5" />
                    <div>
                      <div className="font-medium">{item.name}</div>
                      <div className="text-xs text-gray-500 hidden sm:block">
                        {item.description}
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          </nav>

          {/* Main Content */}
          <main className="flex-1 bg-white rounded-lg shadow-sm">
            {renderContent()}
          </main>
        </div>
      </div>
    </div>
  );
};

export default App;