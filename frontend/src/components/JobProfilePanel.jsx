import { Briefcase, MapPin, GraduationCap, Ban, Sparkles } from "lucide-react";

function Section({ icon, title, items, color }) {
  const Icon = icon;
  return (
    <div className="card p-5">
      <div className={`flex items-center gap-2 font-semibold mb-3 ${color}`}>
        <Icon size={18} /> {title}
      </div>
      <ul className="space-y-1.5 text-sm text-slate-300">
        {(items || []).map((it, i) => (
          <li key={i} className="flex gap-2">
            <span className="text-slate-600">•</span>
            <span>{it}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function JobProfilePanel({ profile }) {
  if (!profile || !profile.role_title)
    return <div className="text-slate-500">Job profile not loaded.</div>;

  const exp = profile.experience || {};
  return (
    <div className="space-y-4">
      <div className="card p-6">
        <div className="flex items-center gap-2 text-brand-300 mb-1">
          <Briefcase size={18} />
          <span className="text-sm uppercase tracking-wide">{profile.company}</span>
        </div>
        <h2 className="text-2xl font-bold">{profile.role_title}</h2>
        <div className="flex flex-wrap gap-3 mt-3 text-sm text-slate-400">
          <span className="flex items-center gap-1">
            <MapPin size={14} /> {(profile.locations || []).join(", ")}
          </span>
          <span className="flex items-center gap-1">
            <Briefcase size={14} /> {exp.ideal_low}-{exp.ideal_high} yrs ideal (
            {exp.min_years}-{exp.max_years} range)
          </span>
          <span>{profile.company_stage}</span>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <Section
          icon={Sparkles}
          title="Required Skills"
          items={profile.required_skills}
          color="text-emerald-400"
        />
        <Section
          icon={Sparkles}
          title="Preferred Skills"
          items={profile.preferred_skills}
          color="text-brand-400"
        />
        <Section
          icon={Briefcase}
          title="Domain Requirements"
          items={profile.domain_requirements}
          color="text-cyan-400"
        />
        <Section
          icon={GraduationCap}
          title="Soft Skills"
          items={profile.soft_skills}
          color="text-amber-400"
        />
      </div>

      <Section
        icon={Ban}
        title="Disqualifiers (what the JD explicitly does NOT want)"
        items={profile.disqualifiers}
        color="text-rose-400"
      />

      {profile.education_requirements && (
        <div className="card p-5">
          <div className="flex items-center gap-2 font-semibold mb-2 text-violet-400">
            <GraduationCap size={18} /> Education
          </div>
          <p className="text-sm text-slate-300">{profile.education_requirements}</p>
        </div>
      )}
    </div>
  );
}
