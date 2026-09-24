import Link from "next/link";

export default function NotFound() {
  return (
    <div className="py-20 text-center">
      <h1 className="text-xl font-semibold text-navy-900">Case not found</h1>
      <Link href="/inbox" className="mt-3 inline-block text-sm text-sky-700 hover:underline">
        Return to inbox
      </Link>
    </div>
  );
}
