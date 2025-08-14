'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

function logout() {
  localStorage.removeItem('token');
}

export default function NavBar() {
  const router = useRouter();
  const [authed, setAuthed] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    setAuthed(!!token);
  }, []);

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  return (
    <nav className="flex gap-4 mb-6">
      {authed ? (
        <>
          <Link href="/upload">Upload</Link>
          <Link href="/documents">Documents</Link>
          <Link href="/search">Search</Link>
          <button onClick={handleLogout}>Logout</button>
        </>
      ) : (
        <>
          <Link href="/login">Login</Link>
          <Link href="/register">Register</Link>
        </>
      )}
    </nav>
  );
}
