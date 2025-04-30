import { Link } from 'react-router-dom';

export default function Header() {
  return (
    <header className="bg-white shadow-md p-4">
      <div className="container mx-auto flex justify-between items-center">
        <Link to="/" className="text-2xl font-bold text-gray-800">
          Traffilyzer
        </Link>
        <nav>
          <ul className="flex space-x-6">
            <li>
              <Link to="/map" className="text-gray-600 hover:text-gray-900">
                Interactive Map
              </Link>
            </li>
            <li>
              <Link
                to="/analysis"
                className="text-gray-600 hover:text-gray-900"
              >
                Analysis
              </Link>
            </li>
          </ul>
        </nav>
      </div>
    </header>
  );
}
