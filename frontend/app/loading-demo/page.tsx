"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Spinner, FullPageLoader, CardLoader, ButtonLoader } from "@/components/ui/spinner";

export default function LoadingDemo() {
  const [showFullPageLoader, setShowFullPageLoader] = useState(false);
  const [buttonLoading, setButtonLoading] = useState(false);

  const handleButtonClick = () => {
    setButtonLoading(true);
    setTimeout(() => setButtonLoading(false), 2000);
  };

  const handleFullPageLoader = () => {
    setShowFullPageLoader(true);
    setTimeout(() => setShowFullPageLoader(false), 3000);
  };

  return (
    <div className="min-h-screen bg-background p-8">
      {showFullPageLoader && <FullPageLoader text="Loading Demo..." subtext="Showcasing themed loading animations" />}
      
      <div className="max-w-6xl mx-auto space-y-8">
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold text-foreground">Loading Animations Demo</h1>
          <p className="text-lg text-muted-foreground">
            Theme-matching loading animations for your RFP automation platform
          </p>
        </div>

        {/* Spinner Variants */}
        <Card className="p-6 space-y-6">
          <h2 className="text-2xl font-semibold text-foreground">Spinner Variants</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="space-y-2">
              <h3 className="text-sm font-medium text-muted-foreground">Default</h3>
              <Spinner size="md" />
              <Spinner size="md" text="Loading..." />
            </div>
            
            <div className="space-y-2">
              <h3 className="text-sm font-medium text-muted-foreground">Dots</h3>
              <Spinner variant="dots" />
              <Spinner variant="dots" text="Processing..." />
            </div>
            
            <div className="space-y-2">
              <h3 className="text-sm font-medium text-muted-foreground">Pulse</h3>
              <Spinner variant="pulse" />
              <Spinner variant="pulse" text="Analyzing..." />
            </div>
            
            <div className="space-y-2">
              <h3 className="text-sm font-medium text-muted-foreground">Glow</h3>
              <Spinner variant="glow" />
              <Spinner variant="glow" text="Generating..." />
            </div>
          </div>

          <div className="space-y-2">
            <h3 className="text-sm font-medium text-muted-foreground">Size Variations</h3>
            <div className="flex items-center gap-4">
              <Spinner size="sm" />
              <Spinner size="md" />
              <Spinner size="lg" />
              <Spinner size="xl" />
            </div>
          </div>
        </Card>

        {/* Button Loader */}
        <Card className="p-6 space-y-4">
          <h2 className="text-2xl font-semibold text-foreground">Button Loader</h2>
          <div className="flex flex-wrap gap-4">
            <ButtonLoader 
              loading={buttonLoading}
              onClick={handleButtonClick}
            >
              {!buttonLoading && "Click to Load"}
            </ButtonLoader>
            
            <ButtonLoader 
              loading={false}
              onClick={() => {}}
              className="bg-transparent border-border hover:bg-secondary text-foreground"
            >
              Outline Button
            </ButtonLoader>
            
            <ButtonLoader 
              loading={false}
              onClick={() => {}}
              className="bg-green-600 hover:bg-green-700 text-white"
            >
              Custom Color
            </ButtonLoader>
          </div>
        </Card>

        {/* Card Loader */}
        <Card className="p-6 space-y-4">
          <h2 className="text-2xl font-semibold text-foreground">Card Loader (Skeleton)</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <CardLoader lines={3} />
            <CardLoader lines={5} />
          </div>
        </Card>

        {/* Full Page Loader Demo */}
        <Card className="p-6 space-y-4">
          <h2 className="text-2xl font-semibold text-foreground">Full Page Loader</h2>
          <p className="text-muted-foreground">
            Click the button below to see the full page loader in action
          </p>
          <Button onClick={handleFullPageLoader}>
            Show Full Page Loader
          </Button>
        </Card>

        {/* Usage Examples */}
        <Card className="p-6 space-y-4">
          <h2 className="text-2xl font-semibold text-foreground">Usage Examples</h2>
          <div className="space-y-4 text-sm">
            <div>
              <h3 className="font-medium text-foreground mb-2">Basic Spinner:</h3>
              <code className="block p-3 bg-secondary rounded text-xs">
{`import { Spinner } from "@/components/ui/spinner"
<Spinner size="md" text="Loading..." />`}
              </code>
            </div>
            
            <div>
              <h3 className="font-medium text-foreground mb-2">Button Loader:</h3>
              <code className="block p-3 bg-secondary rounded text-xs">
{`import { ButtonLoader } from "@/components/ui/spinner"
<ButtonLoader loading={isLoading} onClick={handleSubmit}>
  {!isLoading && "Submit"}
</ButtonLoader>`}
              </code>
            </div>
            
            <div>
              <h3 className="font-medium text-foreground mb-2">Full Page Loader:</h3>
              <code className="block p-3 bg-secondary rounded text-xs">
{`import { FullPageLoader } from "@/components/ui/spinner"
{loading && <FullPageLoader text="Loading..." subtext="Please wait" />}`}
              </code>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
