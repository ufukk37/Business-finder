import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { 
  Building2, 
  Search, 
  Phone, 
  Globe, 
  Star,
  TrendingUp,
  MapPin,
  ArrowRight
} from 'lucide-react';
import { getDashboardStats } from '../services/api';

function StatCard({ icon: Icon, label, value, color, subtext }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-slate-500 mb-1">{label}</p>
          <p className="text-2xl font-bold text-slate-800">{value}</p>
          {subtext && <p className="text-xs text-slate-400 mt-1">{subtext}</p>}
        </div>
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${color}`}>
          <Icon className="w-5 h-5 text-white" />
        </div>
      </div>
    </div>
  );
}

function Dashboard() {
  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: getDashboardStats,
    refetchInterval: 60000, // Her dakika güncelle
  });

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-white rounded-xl border border-slate-200 p-6">
              <div className="skeleton h-4 w-24 rounded mb-2"></div>
              <div className="skeleton h-8 w-16 rounded"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
        Veriler yüklenirken hata oluştu. Lütfen sayfayı yenileyin.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard 
          icon={Building2}
          label="Toplam İşletme"
          value={stats?.total_businesses || 0}
          color="bg-primary-500"
        />
        <StatCard 
          icon={Search}
          label="Toplam Arama"
          value={stats?.total_searches || 0}
          color="bg-emerald-500"
        />
        <StatCard 
          icon={Phone}
          label="Telefonu Olan"
          value={stats?.businesses_with_phone || 0}
          color="bg-amber-500"
          subtext={`${stats?.total_businesses ? Math.round((stats.businesses_with_phone / stats.total_businesses) * 100) : 0}%`}
        />
        <StatCard 
          icon={Star}
          label="Ortalama Puan"
          value={stats?.average_rating?.toFixed(1) || '0.0'}
          color="bg-purple-500"
        />
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Link 
          to="/search"
          className="bg-gradient-to-r from-primary-500 to-primary-600 rounded-xl p-6 text-white hover:from-primary-600 hover:to-primary-700 transition-all group"
        >
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold mb-1">Yeni Arama Yap</h3>
              <p className="text-primary-100 text-sm">İşletmeleri keşfetmeye başla</p>
            </div>
            <ArrowRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
          </div>
        </Link>

        <Link 
          to="/businesses"
          className="bg-white border border-slate-200 rounded-xl p-6 hover:border-primary-300 hover:bg-primary-50/50 transition-all group"
        >
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-slate-800 mb-1">İşletmeleri Görüntüle</h3>
              <p className="text-slate-500 text-sm">Tüm veritabanını incele</p>
            </div>
            <ArrowRight className="w-6 h-6 text-slate-400 group-hover:text-primary-500 group-hover:translate-x-1 transition-all" />
          </div>
        </Link>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Cities */}
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h3 className="font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <MapPin className="w-5 h-5 text-primary-500" />
            En Çok İşletme Olan Şehirler
          </h3>
          <div className="space-y-3">
            {stats?.top_cities?.length > 0 ? (
              stats.top_cities.map((city, index) => (
                <div key={index} className="flex items-center gap-3">
                  <span className="w-6 h-6 rounded-full bg-primary-100 text-primary-700 text-xs font-medium flex items-center justify-center">
                    {index + 1}
                  </span>
                  <span className="flex-1 text-slate-700">{city.city || 'Bilinmiyor'}</span>
                  <span className="text-slate-500 font-medium">{city.count}</span>
                </div>
              ))
            ) : (
              <p className="text-slate-400 text-sm">Henüz veri yok</p>
            )}
          </div>
        </div>

        {/* Top Categories */}
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h3 className="font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-emerald-500" />
            En Popüler Kategoriler
          </h3>
          <div className="space-y-3">
            {stats?.top_categories?.length > 0 ? (
              stats.top_categories.map((cat, index) => (
                <div key={index} className="flex items-center gap-3">
                  <span className="w-6 h-6 rounded-full bg-emerald-100 text-emerald-700 text-xs font-medium flex items-center justify-center">
                    {index + 1}
                  </span>
                  <span className="flex-1 text-slate-700">{cat.category || 'Diğer'}</span>
                  <span className="text-slate-500 font-medium">{cat.count}</span>
                </div>
              ))
            ) : (
              <p className="text-slate-400 text-sm">Henüz veri yok</p>
            )}
          </div>
        </div>
      </div>

      {/* Recent Searches */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h3 className="font-semibold text-slate-800 mb-4 flex items-center gap-2">
          <Search className="w-5 h-5 text-amber-500" />
          Son Aramalar
        </h3>
        {stats?.recent_searches?.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-slate-500 border-b border-slate-100">
                  <th className="pb-3 font-medium">Lokasyon</th>
                  <th className="pb-3 font-medium">Kategori</th>
                  <th className="pb-3 font-medium">Sonuç</th>
                  <th className="pb-3 font-medium">Tarih</th>
                </tr>
              </thead>
              <tbody>
                {stats.recent_searches.map((search, index) => (
                  <tr key={index} className="border-b border-slate-50">
                    <td className="py-3 text-slate-700">{search.location}</td>
                    <td className="py-3 text-slate-700">{search.type}</td>
                    <td className="py-3">
                      <span className="bg-primary-100 text-primary-700 px-2 py-0.5 rounded text-xs font-medium">
                        {search.results} işletme
                      </span>
                    </td>
                    <td className="py-3 text-slate-500">
                      {search.date ? new Date(search.date).toLocaleDateString('tr-TR') : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-slate-400 text-sm">Henüz arama yapılmadı</p>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
