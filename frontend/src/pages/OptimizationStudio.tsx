import { useState } from "react";
import { 
  SlidersHorizontal, 
  Play, 
  Loader2, 
  CheckCircle, 
  Users, 
  MapPin,
  Cpu,
  Clock,
  Zap,
  BarChart3
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";

const optimizationSteps = [
  "Initializing cluster centroids...",
  "Loading student coordinates...",
  "Allocating Clusters...",
  "Calculating Haversine Distances...",
  "Optimizing bus routes...",
  "Validating capacity constraints...",
  "Generating route manifests...",
];

export default function OptimizationStudio() {
  const [busCapacity, setBusCapacity] = useState([45]);
  const [walkingDistance, setWalkingDistance] = useState([1.5]);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [isComplete, setIsComplete] = useState(false);

  const handleOptimize = () => {
    setIsOptimizing(true);
    setIsComplete(false);
    setCurrentStep(0);

    // Simulate optimization steps
    optimizationSteps.forEach((_, index) => {
      setTimeout(() => {
        setCurrentStep(index + 1);
        if (index === optimizationSteps.length - 1) {
          setTimeout(() => {
            setIsOptimizing(false);
            setIsComplete(true);
          }, 800);
        }
      }, (index + 1) * 1200);
    });
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground">Optimization Studio</h1>
        <p className="text-muted-foreground text-sm mt-1">Configure and execute ML-powered route optimization</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Algorithm Tuning Panel */}
        <Card className="glass lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <SlidersHorizontal className="h-5 w-5 text-accent" />
              Algorithm Parameters
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-8">
            {/* Bus Capacity Slider */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-primary/10">
                    <Users className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <p className="font-medium text-foreground">Bus Capacity</p>
                    <p className="text-xs text-muted-foreground">Maximum students per bus</p>
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-3xl font-bold text-foreground font-mono">{busCapacity[0]}</span>
                  <span className="text-sm text-muted-foreground ml-1">students</span>
                </div>
              </div>
              <div className="px-2">
                <Slider
                  value={busCapacity}
                  onValueChange={setBusCapacity}
                  min={10}
                  max={80}
                  step={5}
                  className="w-full"
                />
                <div className="flex justify-between mt-2 text-xs text-muted-foreground">
                  <span>10</span>
                  <span>45 (recommended)</span>
                  <span>80</span>
                </div>
              </div>
            </div>

            {/* Walking Distance Slider */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-accent/10">
                    <MapPin className="h-5 w-5 text-accent" />
                  </div>
                  <div>
                    <p className="font-medium text-foreground">Max Walking Distance</p>
                    <p className="text-xs text-muted-foreground">Maximum distance to bus stop</p>
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-3xl font-bold text-foreground font-mono">{walkingDistance[0].toFixed(1)}</span>
                  <span className="text-sm text-muted-foreground ml-1">km</span>
                </div>
              </div>
              <div className="px-2">
                <Slider
                  value={walkingDistance}
                  onValueChange={setWalkingDistance}
                  min={0.5}
                  max={3}
                  step={0.1}
                  className="w-full"
                />
                <div className="flex justify-between mt-2 text-xs text-muted-foreground">
                  <span>0.5km</span>
                  <span>1.5km (recommended)</span>
                  <span>3km</span>
                </div>
              </div>
            </div>

            {/* Run Button */}
            <div className="pt-4">
              <Button
                onClick={handleOptimize}
                disabled={isOptimizing}
                className="w-full h-14 text-lg font-semibold bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70 glow-red transition-all duration-300"
                size="lg"
              >
                {isOptimizing ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    Optimizing...
                  </>
                ) : isComplete ? (
                  <>
                    <CheckCircle className="mr-2 h-5 w-5" />
                    Optimization Complete — Run Again
                  </>
                ) : (
                  <>
                    <Play className="mr-2 h-5 w-5" />
                    RUN OPTIMIZER
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Execution Status Panel */}
        <Card className="glass">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Cpu className="h-5 w-5 text-accent" />
              Execution Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {optimizationSteps.map((step, index) => {
                const isActive = isOptimizing && currentStep === index + 1;
                const isCompleted = currentStep > index + 1 || isComplete;
                const isPending = currentStep <= index && !isComplete;

                return (
                  <div 
                    key={index}
                    className={`flex items-center gap-3 p-3 rounded-lg transition-all duration-300 ${
                      isActive ? 'bg-accent/10 border border-accent/30' :
                      isCompleted ? 'bg-success/10' : 'bg-secondary/30'
                    }`}
                  >
                    <div className={`h-6 w-6 rounded-full flex items-center justify-center flex-shrink-0 ${
                      isActive ? 'bg-accent/20' :
                      isCompleted ? 'bg-success/20' : 'bg-secondary'
                    }`}>
                      {isActive && <Loader2 className="h-3.5 w-3.5 text-accent animate-spin" />}
                      {isCompleted && <CheckCircle className="h-3.5 w-3.5 text-success" />}
                      {isPending && !isActive && <span className="text-xs text-muted-foreground">{index + 1}</span>}
                    </div>
                    <span className={`text-sm ${
                      isActive ? 'text-accent font-medium' :
                      isCompleted ? 'text-success' : 'text-muted-foreground'
                    }`}>
                      {step}
                    </span>
                  </div>
                );
              })}
            </div>

            {isComplete && (
              <div className="mt-6 p-4 rounded-lg bg-success/10 border border-success/20">
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle className="h-5 w-5 text-success" />
                  <span className="font-medium text-success">Optimization Complete</span>
                </div>
                <div className="grid grid-cols-2 gap-4 mt-4">
                  <div>
                    <p className="text-xs text-muted-foreground">Time Elapsed</p>
                    <p className="text-lg font-semibold text-foreground font-mono">8.4s</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Routes Generated</p>
                    <p className="text-lg font-semibold text-foreground font-mono">24</p>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: "Last Run", value: "Today, 9:42 AM", icon: Clock },
          { label: "Model Version", value: "v2.4.1", icon: Cpu },
          { label: "Avg Runtime", value: "8.2 seconds", icon: Zap },
          { label: "Success Rate", value: "99.8%", icon: BarChart3 },
        ].map((stat) => (
          <Card key={stat.label} className="glass-subtle">
            <CardContent className="p-4 flex items-center gap-4">
              <div className="p-2 rounded-lg bg-secondary">
                <stat.icon className="h-4 w-4 text-muted-foreground" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">{stat.label}</p>
                <p className="text-sm font-semibold text-foreground">{stat.value}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
