// layout.hpp
/*
  neogfx C++ GUI Library
  Copyright(C) 2016 Leigh Johnston
  
  This program is free software: you can redistribute it and / or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.
  
  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.
  
  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#pragma once

#include "neogfx.hpp"
#include <list>
#include <neolib/variant.hpp>
#include "i_layout.hpp"

namespace neogfx
{
	class i_spacer;

	class layout : public i_layout
	{
	public:
		struct widget_already_added : std::logic_error { widget_already_added() : std::logic_error("neogfx::layout::widget_already_added") {} };
	protected:
		class item : public i_geometry
		{
		public:
			typedef std::shared_ptr<i_widget> widget_pointer;
			typedef std::shared_ptr<i_layout> layout_pointer;
			typedef std::shared_ptr<i_spacer> spacer_pointer;
			typedef neolib::variant<widget_pointer, layout_pointer, spacer_pointer> pointer_wrapper;
		public:
			item(i_widget& aWidget);
			item(std::shared_ptr<i_widget> aWidget);
			item(i_layout& aLayout);
			item(std::shared_ptr<i_layout> aLayout);
			item(i_spacer& aSpacer);
			item(std::shared_ptr<i_spacer> aSpacer);
		public:
			const pointer_wrapper& get() const;
			pointer_wrapper& get();
			void set_owner(i_widget* aOwner);
			void layout(const point& aPosition, const size& aSize);
		public:
			virtual bool has_minimum_size() const;
			virtual size minimum_size() const;
			virtual void set_minimum_size(const optional_size& aMinimumSize, bool aUpdateLayout = true);
			virtual bool has_maximum_size() const;
			virtual size maximum_size() const;
			virtual void set_maximum_size(const optional_size& aMaximumSize, bool aUpdateLayout = true);
			virtual bool is_fixed_size() const;
			virtual void set_fixed_size(const optional_size& aFixedSize, bool aUpdateLayout = true);
		public:
			virtual bool has_margins() const;
			virtual neogfx::margins margins() const;
			virtual void set_margins(const optional_margins& aMargins);
		public:
			bool visible() const;
		private:
			pointer_wrapper iPointerWrapper;
			i_widget* iOwner;
		};
		typedef std::list<item> item_list;
		enum item_type_e
		{
			ItemTypeWidget = 0x01,
			ItemTypeLayout = 0x02,
			ItemTypeSpacer = 0x04
		};
	private:
		class device_metrics_forwarder : public i_device_metrics
		{
		public:
			device_metrics_forwarder(i_layout& aOwner);
		public:
			virtual size extents() const;
			virtual dimension horizontal_dpi() const;
			virtual dimension vertical_dpi() const;
			virtual dimension em_size() const;
		private:
			i_layout& iOwner;
		};
	public:
		layout(i_widget& aParent);
		layout(i_layout& aParent);
	public:
		virtual i_widget* owner() const;
		virtual void set_owner(i_widget* aOwner);
		virtual void add_widget(i_widget& aWidget);
		virtual void add_widget(uint32_t aPosition, i_widget& aWidget);
		virtual void add_widget(std::shared_ptr<i_widget> aWidget);
		virtual void add_widget(uint32_t aPosition, std::shared_ptr<i_widget> aWidget);
		virtual void add_layout(i_layout& aLayout);
		virtual void add_layout(uint32_t aPosition, i_layout& aLayout);
		virtual void add_layout(std::shared_ptr<i_layout> aLayout);
		virtual void add_layout(uint32_t aPosition, std::shared_ptr<i_layout> aLayout);
		virtual void add_spacer(i_spacer& aSpacer);
		virtual void add_spacer(uint32_t aPosition, i_spacer& aSpacer);
		virtual void add_spacer(std::shared_ptr<i_spacer> aSpacer);
		virtual void add_spacer(uint32_t aPosition, std::shared_ptr<i_spacer> aSpacer);
		virtual void remove_item(std::size_t aIndex);
		virtual std::size_t item_count() const;
		virtual i_geometry& get_item(std::size_t aIndex);
		using i_layout::get_widget;
		virtual i_widget& get_widget(std::size_t aIndex);
		virtual i_layout& get_layout(std::size_t aIndex);
	public:
		virtual bool has_margins() const;
		virtual neogfx::margins margins() const;
		virtual void set_margins(const optional_margins& aMargins);
	public:
		virtual size spacing() const;
		virtual void set_spacing(dimension aSpacing);
		virtual void set_spacing(size aSpacing);
	public:
		virtual void enable();
		virtual void disable();
		virtual bool enabled() const;
	public:
		virtual bool has_minimum_size() const;
		virtual size minimum_size() const;
		virtual void set_minimum_size(const optional_size& aMinimumSize, bool aUpdateLayout = true);
		virtual bool has_maximum_size() const;
		virtual size maximum_size() const;
		virtual void set_maximum_size(const optional_size& aMaximumSize, bool aUpdateLayout = true);
		virtual bool is_fixed_size() const;
		virtual void set_fixed_size(const optional_size& aFixedSize, bool aUpdateLayout = true);
	public:
		virtual const i_device_metrics& device_metrics() const;
		virtual units_e units() const;
		virtual units_e set_units(units_e aUnits) const;
	protected:
		const item_list& items() const;
		item_list& items();
		const i_geometry& item_geometry(item_list::size_type aItem) const;
		uint32_t spacer_count() const;
		uint32_t items_visible(item_type_e aItemType = static_cast<item_type_e>(ItemTypeWidget|ItemTypeLayout)) const;
	private:
		i_widget* iOwner;
		device_metrics_forwarder iDeviceMetricsForwarder;
		units_context iUnitsContext;
		optional_margins iMargins;
		size iSpacing;
		bool iEnabled;
		optional_size iMinimumSize;
		optional_size iMaximumSize;
		item_list iItems;
		bool iLayoutStarted;
	};
}