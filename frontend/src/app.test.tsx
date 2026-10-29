import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { vi, test, expect } from 'vitest';
import App from './App';
test('renders operational dashboard without silently substituting data on API failure',async()=>{
 vi.stubGlobal('fetch',vi.fn().mockRejectedValue(new Error('offline')));
 const client=new QueryClient({defaultOptions:{queries:{retry:false}}});
 render(<QueryClientProvider client={client}><App/></QueryClientProvider>);
 expect(screen.getByRole('heading',{name:'Overview'})).toBeTruthy();
 expect(await screen.findByText(/API unavailable/)).toBeTruthy();
 expect(await screen.findByText(/No matching events\.|Could not load events\./)).toBeTruthy();
});
