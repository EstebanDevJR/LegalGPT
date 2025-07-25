import React, { useState, useEffect } from 'react';
import { 
  Scale, 
  MessageSquare, 
  FileText, 
  Shield, 
  Users, 
  Menu, 
  X,
  ChevronRight,
  Star,
  Building2,
  CheckCircle
} from 'lucide-react';
import Chat from './components/Chat';
import { ragAPI } from './lib/api';
import { cn } from './lib/utils';

type ViewType = 'home' | 'chat' | 'about' | 'features';

function App() {
  const [currentView, setCurrentView] = useState<ViewType>('home');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [serviceHealth, setServiceHealth] = useState<{
    status: string;
    estimated_response_time_seconds: string;
  } | null>(null);

  useEffect(() => {
    // Verificar estado del servicio
    checkServiceHealth();
  }, []);

  const checkServiceHealth = async () => {
    try {
      const health = await ragAPI.healthCheck();
      setServiceHealth(health);
    } catch (error) {
      console.error('Service health check failed:', error);
    }
  };

  const navigation = [
    { name: 'Inicio', id: 'home' as ViewType, icon: Building2 },
    { name: 'Chat Legal', id: 'chat' as ViewType, icon: MessageSquare },
    { name: 'Características', id: 'features' as ViewType, icon: Star },
    { name: 'Acerca de', id: 'about' as ViewType, icon: FileText },
  ];

  const features = [
    {
      icon: Scale,
      title: 'Asesoría Legal Especializada',
      description: 'Consultas especializadas en legislación colombiana para PyMEs.',
      color: 'text-blue-600'
    },
    {
      icon: Shield,
      title: 'Información Confiable',
      description: 'Respuestas basadas en fuentes oficiales y legislación actualizada.',
      color: 'text-green-600'
    },
    {
      icon: FileText,
      title: 'Análisis de Documentos',
      description: 'Revisión automática de contratos y documentos legales.',
      color: 'text-purple-600'
    },
    {
      icon: Users,
      title: 'Para PyMEs Colombianas',
      description: 'Optimizado específicamente para micro, pequeñas y medianas empresas.',
      color: 'text-orange-600'
    },
  ];

  const categories = [
    { name: '🏪 Constitución de Empresa', description: 'SAS, Ltda, trámites legales' },
    { name: '💼 Derecho Laboral', description: 'Contratos, prestaciones, liquidaciones' },
    { name: '🏛️ Obligaciones Tributarias', description: 'DIAN, declaraciones, régimenes' },
    { name: '🏢 Contratos Comerciales', description: 'Cláusulas, riesgos, negociación' },
  ];

  const renderHomeView = () => (
    <div className="space-y-16">
      {/* Hero Section */}
      <section className="text-center space-y-6 py-16">
        <div className="flex justify-center mb-6">
          <div className="w-20 h-20 bg-primary rounded-2xl flex items-center justify-center">
            <Scale className="w-10 h-10 text-primary-foreground" />
          </div>
        </div>
        <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent">
          LegalGPT
        </h1>
        <p className="text-xl md:text-2xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
          Tu asistente legal inteligente especializado en PyMEs colombianas
        </p>
        <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
          Obtén asesoría legal confiable sobre constitución de empresas, derecho laboral, 
          obligaciones tributarias y análisis de documentos.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center mt-8">
          <button
            onClick={() => setCurrentView('chat')}
            className="btn-primary px-8 py-3 text-lg flex items-center gap-2"
          >
            <MessageSquare className="w-5 h-5" />
            Iniciar Consulta
            <ChevronRight className="w-4 h-4" />
          </button>
          <button
            onClick={() => setCurrentView('features')}
            className="btn-secondary px-8 py-3 text-lg"
          >
            Ver Características
          </button>
        </div>
      </section>

      {/* Service Status */}
      {serviceHealth && (
        <section className="bg-muted/50 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={cn(
                'w-3 h-3 rounded-full',
                serviceHealth.status === 'healthy' ? 'bg-green-500' : 'bg-yellow-500'
              )} />
              <span className="font-medium">
                Estado del Servicio: {serviceHealth.status === 'healthy' ? 'Operativo' : 'Limitado'}
              </span>
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-300">
              Tiempo de respuesta: {serviceHealth.estimated_response_time_seconds}
            </div>
          </div>
        </section>
      )}

      {/* Features Grid */}
      <section className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
        {features.map((feature, index) => (
          <div key={index} className="card p-6 text-center hover:shadow-lg transition-shadow">
            <feature.icon className={cn('w-12 h-12 mx-auto mb-4', feature.color)} />
            <h3 className="font-semibold mb-2">{feature.title}</h3>
            <p className="text-sm text-gray-600 dark:text-gray-300">{feature.description}</p>
          </div>
        ))}
      </section>

      {/* Categories */}
      <section className="space-y-6">
        <div className="text-center">
          <h2 className="text-3xl font-bold mb-4">Áreas de Especialización</h2>
          <p className="text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            LegalGPT está optimizado para ayudar a PyMEs colombianas en las siguientes áreas legales:
          </p>
        </div>
        <div className="grid md:grid-cols-2 gap-4">
          {categories.map((category, index) => (
            <div key={index} className="card p-6 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors cursor-pointer"
                 onClick={() => setCurrentView('chat')}>
              <div className="flex items-center gap-3">
                <CheckCircle className="w-5 h-5 text-green-600" />
                <div>
                  <h3 className="font-semibold">{category.name}</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-300">{category.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-primary text-primary-foreground rounded-lg p-8 text-center">
        <h2 className="text-2xl font-bold mb-4">
          ¿Listo para obtener asesoría legal confiable?
        </h2>
        <p className="mb-6 opacity-90">
          Comienza tu consulta legal ahora mismo. Es rápido, fácil y está optimizado para PyMEs colombianas.
        </p>
        <button
          onClick={() => setCurrentView('chat')}
          className="bg-white text-primary hover:bg-gray-100 px-8 py-3 rounded-md font-medium transition-colors"
        >
          Iniciar Consulta Gratuita
        </button>
      </section>
    </div>
  );

  const renderFeaturesView = () => (
    <div className="space-y-12">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">Características de LegalGPT</h1>
        <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
          Descubre todas las funcionalidades que hacen de LegalGPT la mejor opción para asesoría legal de PyMEs
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-12">
        {features.map((feature, index) => (
          <div key={index} className="card p-8">
            <feature.icon className={cn('w-16 h-16 mb-6', feature.color)} />
            <h3 className="text-2xl font-semibold mb-4">{feature.title}</h3>
            <p className="text-gray-600 dark:text-gray-300 text-lg leading-relaxed">{feature.description}</p>
          </div>
        ))}
      </div>

      <div className="text-center">
        <button
          onClick={() => setCurrentView('chat')}
          className="btn-primary px-8 py-3 text-lg"
        >
          Probar Ahora
        </button>
      </div>
    </div>
  );

  const renderAboutView = () => (
    <div className="space-y-8 max-w-4xl mx-auto">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">Acerca de LegalGPT</h1>
        <p className="text-xl text-gray-600 dark:text-gray-300">
          Tu asistente legal inteligente para PyMEs colombianas
        </p>
      </div>

      <div className="prose prose-lg max-w-none space-y-6">
        <section className="card p-8">
          <h2 className="text-2xl font-semibold mb-4">¿Qué es LegalGPT?</h2>
          <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
            LegalGPT es un asistente legal inteligente específicamente diseñado para ayudar a micro, 
            pequeñas y medianas empresas (PyMEs) en Colombia. Utilizando inteligencia artificial avanzada, 
            proporcionamos asesoría legal confiable y actualizada sobre temas cruciales para el 
            desarrollo empresarial.
          </p>
        </section>

        <section className="card p-8">
          <h2 className="text-2xl font-semibold mb-4">¿Por qué LegalGPT?</h2>
          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-600 mt-1" />
              <div>
                <strong>Especialización en PyMEs:</strong> Optimizado específicamente para las necesidades 
                de micro, pequeñas y medianas empresas colombianas.
              </div>
            </div>
            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-600 mt-1" />
              <div>
                <strong>Legislación Actualizada:</strong> Basado en las leyes y regulaciones 
                más recientes de Colombia.
              </div>
            </div>
            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-600 mt-1" />
              <div>
                <strong>Acceso 24/7:</strong> Disponible cuando lo necesites, 
                sin citas ni horarios de atención.
              </div>
            </div>
            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-600 mt-1" />
              <div>
                <strong>Análisis de Documentos:</strong> Capacidad de revisar y analizar 
                contratos y documentos legales.
              </div>
            </div>
          </div>
        </section>

        <section className="card p-8">
          <h2 className="text-2xl font-semibold mb-4">Limitaciones Importantes</h2>
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <p className="text-yellow-800">
              <strong>Aviso Legal:</strong> LegalGPT proporciona información general y orientación educativa. 
              No constituye asesoría legal profesional y no reemplaza la consulta con un abogado licenciado. 
              Para asuntos legales complejos o críticos, siempre consulte con un profesional del derecho.
            </p>
          </div>
        </section>
      </div>
    </div>
  );

  const currentViewComponent = () => {
    switch (currentView) {
      case 'home':
        return renderHomeView();
      case 'chat':
        return <Chat className="h-[calc(100vh-8rem)]" />;
      case 'features':
        return renderFeaturesView();
      case 'about':
        return renderAboutView();
      default:
        return renderHomeView();
    }
  };

  return (
        <div className="min-h-screen bg-white dark:bg-slate-900">
      {/* Navigation */}
      <nav className="border-b bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60 sticky top-0 z-50 dark:bg-slate-900/95">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="flex items-center gap-2">
                <Scale className="w-8 h-8 text-blue-600" />
                <span className="text-xl font-bold">LegalGPT</span>
              </div>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8">
              {navigation.map((item) => (
                <button
                  key={item.id}
                  onClick={() => setCurrentView(item.id)}
                                   className={cn(
                   'flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors',
                   currentView === item.id
                     ? 'text-blue-600 bg-blue-50 dark:bg-blue-900/20'
                     : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-100 dark:hover:bg-gray-800'
                 )}
                >
                  <item.icon className="w-4 h-4" />
                  {item.name}
                </button>
              ))}
            </div>

            {/* Mobile menu button */}
            <div className="md:hidden flex items-center">
              <button
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                className="p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-100 dark:hover:bg-gray-800"
              >
                {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMobileMenuOpen && (
          <div className="md:hidden border-t bg-background">
            <div className="px-2 pt-2 pb-3 space-y-1">
              {navigation.map((item) => (
                <button
                  key={item.id}
                  onClick={() => {
                    setCurrentView(item.id);
                    setIsMobileMenuOpen(false);
                  }}
                                     className={cn(
                     'flex items-center gap-2 w-full px-3 py-2 rounded-md text-sm font-medium transition-colors',
                     currentView === item.id
                       ? 'text-blue-600 bg-blue-50 dark:bg-blue-900/20'
                       : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-100 dark:hover:bg-gray-800'
                   )}
                >
                  <item.icon className="w-4 h-4" />
                  {item.name}
                </button>
              ))}
            </div>
          </div>
        )}
      </nav>

      {/* Main Content */}
      <main className={cn(
        'max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8',
        currentView === 'chat' ? 'max-w-none px-0 py-0' : ''
      )}>
        {currentViewComponent()}
      </main>

      {/* Footer */}
      {currentView !== 'chat' && (
        <footer className="border-t bg-gray-50 dark:bg-gray-900 mt-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="text-center text-sm text-gray-600 dark:text-gray-300">
              <p>© 2024 LegalGPT. Diseñado para PyMEs colombianas.</p>
              <p className="mt-2">
                <strong>Aviso:</strong> Esta herramienta proporciona información general. 
                No constituye asesoría legal profesional.
              </p>
            </div>
          </div>
        </footer>
      )}
    </div>
  );
}

export default App;
