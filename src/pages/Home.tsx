import React from "react";
import { ChatInterfaceWithSidebar } from "../components/ChatInterfaceWithSidebar";

const Home: React.FC = () => (
  <main style={{ padding: 0, height: '100vh' }}>
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <ChatInterfaceWithSidebar />
    </div>
  </main>
);

export default Home;
